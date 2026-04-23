from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from statistics import mean
from typing import Any

from sqlalchemy.orm import Session

from app.models.exercise import DifficultyLevel, Exercise, ExerciseType, SourceType
from app.models.exercise_attempt import ExerciseAttempt, SubmissionStatus
from app.models.exercise_evaluation import ExerciseEvaluation
from app.models.user import User
from app.models.user_topic_mastery import UserTopicMastery
from app.schemas.exercise import ExerciseGenerateRequest


@dataclass
class GeneratedExercisePayload:
    title: str
    prompt_markdown: str
    constraints_json: dict[str, Any]
    expected_outcomes_json: list[str]
    hints_json: list[str]
    canonical_solution_json: dict[str, Any]
    tags: list[str]


def _difficulty_prefix(difficulty: DifficultyLevel) -> str:
    return {
        DifficultyLevel.easy: "Foundational",
        DifficultyLevel.medium: "Applied",
        DifficultyLevel.hard: "Stretch",
    }[difficulty]


def build_generated_exercise(payload: ExerciseGenerateRequest, weak_topics: list[str]) -> GeneratedExercisePayload:
    role = payload.context.target_role or "software engineer"
    focus_topics = ", ".join(weak_topics[:2]) if weak_topics else "clear trade-off reasoning"
    subtopic = payload.subtopic or payload.topic
    title = f"{_difficulty_prefix(payload.difficulty)} {payload.type.value.replace('_', ' ').title()} on {subtopic.title()}"
    prompt_markdown = (
        f"You are preparing for a **{role}** path.\n\n"
        f"Design a solution for **{subtopic}** within the context of **{payload.topic}**.\n\n"
        f"Your answer should address the requested difficulty, justify trade-offs, and show how you would approach it in a real engineering setting."
    )
    constraints_json = {
        "timeLimitMinutes": payload.time_limit_minutes,
        "mustConsider": [payload.topic, subtopic, focus_topics],
        "forbidden": ["hand-wavy reasoning", "skipping edge cases"],
    }
    expected_outcomes_json = [
        f"Demonstrates {payload.topic} reasoning",
        "Explains trade-offs clearly",
        "Provides a structured solution path",
    ]
    hints_json = (
        [
            f"Break {subtopic} into two or three design decisions.",
            "State the constraints before choosing an approach.",
            f"Call out how you would avoid repeating mistakes in {focus_topics}.",
        ]
        if payload.include_hints
        else []
    )
    canonical_solution_json = {
        "summary": f"Strong answers for {subtopic} balance correctness, clarity, and trade-offs.",
        "steps": [
            "Frame the requirements and constraints",
            "Describe the core approach",
            "Evaluate trade-offs and edge cases",
        ],
        "complexity": {
            "time": "Context dependent",
            "space": "Context dependent",
        },
        "tradeOffs": ["clarity vs completeness", "speed vs robustness"],
    }
    tags = [payload.topic, subtopic, payload.type.value.replace("_", "-"), payload.difficulty.value]
    return GeneratedExercisePayload(
        title=title,
        prompt_markdown=prompt_markdown,
        constraints_json=constraints_json,
        expected_outcomes_json=expected_outcomes_json,
        hints_json=hints_json,
        canonical_solution_json=canonical_solution_json,
        tags=tags,
    )


def create_exercise_from_request(
    db: Session,
    user: User,
    payload: ExerciseGenerateRequest,
    weak_topics: list[str],
) -> Exercise:
    generated = build_generated_exercise(payload, weak_topics)
    exercise = Exercise(
        user_id=user.id,
        type=payload.type,
        topic=payload.topic,
        subtopic=payload.subtopic,
        difficulty=payload.difficulty,
        title=generated.title,
        prompt_markdown=generated.prompt_markdown,
        constraints_json=generated.constraints_json,
        expected_outcomes_json=generated.expected_outcomes_json,
        hints_json=generated.hints_json,
        canonical_solution_json=generated.canonical_solution_json,
        tags=generated.tags,
        source=SourceType.ai_generated,
        created_by_ai=True,
    )
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise


def evaluate_attempt(attempt: ExerciseAttempt) -> dict[str, Any]:
    material = "\n".join(
        value for value in [attempt.answer_markdown, attempt.answer_code, attempt.answer_sql] if value
    )
    lower = material.lower()
    length_score = min(10, max(1, len(material) // 90)) if material else 0

    rubric_scores = {
        "correctness": min(10, length_score + (2 if "trade-off" in lower or "tradeoff" in lower else 0)),
        "efficiency": min(10, length_score + (2 if "o(" in lower or "latency" in lower else 0)),
        "clarity": min(10, length_score + (2 if "\n" in material or "-" in material else 0)),
        "tradeOffReasoning": min(10, length_score + (3 if "because" in lower else 0)),
        "maintainability": min(10, length_score + (2 if "test" in lower or "monitor" in lower else 0)),
    }
    overall_score = round(mean(rubric_scores.values()), 2)
    weakest_dimension = min(rubric_scores, key=rubric_scores.get)

    strengths = [
        f"Best score in {dimension}" for dimension, score in rubric_scores.items() if score >= 7
    ] or ["Shows effort toward a structured answer"]
    weaknesses = [
        f"Needs stronger {dimension}" for dimension, score in rubric_scores.items() if score <= 5
    ] or ["Keep tightening trade-off explanations"]
    recommended_next_topics = [attempt.exercise.topic]
    if attempt.exercise.subtopic:
        recommended_next_topics.append(attempt.exercise.subtopic)
    if weakest_dimension == "efficiency":
        recommended_next_topics.append("performance analysis")
    elif weakest_dimension == "tradeOffReasoning":
        recommended_next_topics.append("trade-off analysis")
    else:
        recommended_next_topics.append(weakest_dimension)

    return {
        "overall_score": overall_score,
        "rubric_scores_json": rubric_scores,
        "strengths_json": strengths,
        "weaknesses_json": weaknesses,
        "feedback_markdown": (
            f"Your submission scored **{overall_score}/10** overall.\n\n"
            f"Strongest area: **{max(rubric_scores, key=rubric_scores.get)}**.\n"
            f"Primary gap: **{weakest_dimension}**.\n\n"
            "Tighten the explanation, justify trade-offs more explicitly, and ground the answer in concrete engineering choices."
        ),
        "recommended_next_topics": recommended_next_topics,
        "improvement_actions_json": [
            {
                "action": f"Rework the answer focusing on {weakest_dimension}",
                "why": "That is the lowest-scoring rubric dimension.",
            }
        ],
        "weakest_dimension": weakest_dimension,
    }


def persist_evaluation(db: Session, attempt: ExerciseAttempt) -> ExerciseEvaluation:
    result = evaluate_attempt(attempt)
    evaluation = ExerciseEvaluation(
        attempt_id=attempt.id,
        overall_score=result["overall_score"],
        rubric_scores_json=result["rubric_scores_json"],
        strengths_json=result["strengths_json"],
        weaknesses_json=result["weaknesses_json"],
        feedback_markdown=result["feedback_markdown"],
        recommended_next_topics=result["recommended_next_topics"],
        improvement_actions_json=result["improvement_actions_json"],
        evaluator_type="system",
        prompt_version="epic2-v1",
        model_name="deterministic-rubric",
    )
    db.add(evaluation)
    attempt.status = SubmissionStatus.evaluated
    attempt.evaluated_at = datetime.now(timezone.utc)

    mastery = (
        db.query(UserTopicMastery)
        .filter(
            UserTopicMastery.user_id == attempt.user_id,
            UserTopicMastery.topic == attempt.exercise.topic,
        )
        .one_or_none()
    )
    if mastery is None:
        mastery = UserTopicMastery(
            user_id=attempt.user_id,
            topic=attempt.exercise.topic,
            attempts_count=1,
            average_score=result["overall_score"],
            weakest_dimension=result["weakest_dimension"],
        )
        db.add(mastery)
    else:
        total_score = mastery.average_score * mastery.attempts_count + result["overall_score"]
        mastery.attempts_count += 1
        mastery.average_score = round(total_score / mastery.attempts_count, 2)
        mastery.weakest_dimension = result["weakest_dimension"]

    db.commit()
    db.refresh(evaluation)
    db.refresh(attempt)
    return evaluation
