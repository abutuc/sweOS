from app.models.exercise import DifficultyLevel, ExerciseType
from app.schemas.exercise import ExerciseGenerationContext, ExerciseGenerateRequest
from app.services.exercise_engine import build_generated_exercise


def test_generated_exercise_marks_review_mode_for_weak_topic():
    payload = ExerciseGenerateRequest(
        type=ExerciseType.system_design,
        topic="distributed systems",
        subtopic="rate limiting",
        difficulty=DifficultyLevel.medium,
        include_hints=True,
        context=ExerciseGenerationContext(weak_topics=["distributed systems", "trade-off analysis"]),
    )

    exercise = build_generated_exercise(payload, weak_topics=payload.context.weak_topics)

    assert exercise.constraints_json["reviewMode"] is True
    assert "review-mode" in exercise.tags
    assert "intentionally resurfaces a weaker topic" in exercise.prompt_markdown


def test_generated_exercise_leaves_review_mode_off_without_matching_weak_topic():
    payload = ExerciseGenerateRequest(
        type=ExerciseType.system_design,
        topic="scalability",
        subtopic="rate limiting",
        difficulty=DifficultyLevel.medium,
        include_hints=True,
        context=ExerciseGenerationContext(weak_topics=["distributed systems"]),
    )

    exercise = build_generated_exercise(payload, weak_topics=payload.context.weak_topics)

    assert exercise.constraints_json["reviewMode"] is False
    assert "review-mode" not in exercise.tags
