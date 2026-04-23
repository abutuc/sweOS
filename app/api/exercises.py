import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session, require_current_user
from app.models.exercise import DifficultyLevel, Exercise, ExerciseType
from app.models.exercise_attempt import ExerciseAttempt, SubmissionStatus
from app.models.user import User
from app.models.user_topic_mastery import UserTopicMastery
from app.schemas.exercise import (
    ExerciseAttemptCreateRequest,
    ExerciseAttemptEnvelope,
    ExerciseAttemptEnvelopeData,
    ExerciseAttemptRead,
    ExerciseDetailEnvelope,
    ExerciseEvaluationEnvelope,
    ExerciseEvaluationRead,
    ExerciseGenerateEnvelope,
    ExerciseGenerateRequest,
    ExerciseListEnvelope,
    ExerciseRead,
    ExerciseSummary,
    TopicMasteryEnvelope,
    TopicMasteryRead,
)
from app.services.exercise_engine import create_exercise_from_request, persist_evaluation


router = APIRouter(tags=["exercises"])


def _serialize_exercise(exercise: Exercise) -> ExerciseRead:
    return ExerciseRead(
        id=exercise.id,
        type=exercise.type,
        topic=exercise.topic,
        subtopic=exercise.subtopic,
        difficulty=exercise.difficulty,
        title=exercise.title,
        prompt_markdown=exercise.prompt_markdown,
        constraints=exercise.constraints_json,
        expectedOutcomes=exercise.expected_outcomes_json,
        hints=exercise.hints_json,
        tags=exercise.tags,
        created_at=exercise.created_at,
    )


@router.post("/exercises/generate", response_model=ExerciseGenerateEnvelope)
def generate_exercise(
    payload: ExerciseGenerateRequest,
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> ExerciseGenerateEnvelope:
    weak_topics = (
        payload.context.weak_topics
        or [
            mastery.topic
            for mastery in db.query(UserTopicMastery)
            .filter(UserTopicMastery.user_id == user.id)
            .order_by(UserTopicMastery.average_score.asc(), UserTopicMastery.attempts_count.desc())
            .limit(3)
            .all()
        ]
    )
    exercise = create_exercise_from_request(db, user, payload, weak_topics)
    return ExerciseGenerateEnvelope(data={"exercise": _serialize_exercise(exercise)})


@router.get("/exercises", response_model=ExerciseListEnvelope)
def list_exercises(
    type: ExerciseType | None = Query(default=None),
    topic: str | None = Query(default=None),
    difficulty: DifficultyLevel | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> ExerciseListEnvelope:
    query = db.query(Exercise).filter(Exercise.user_id == user.id)
    if type:
        query = query.filter(Exercise.type == type)
    if topic:
        query = query.filter(Exercise.topic == topic)
    if difficulty:
        query = query.filter(Exercise.difficulty == difficulty)

    total = query.count()
    exercises = query.order_by(Exercise.created_at.desc()).offset(offset).limit(limit).all()
    return ExerciseListEnvelope(
        data=[ExerciseSummary.model_validate(exercise) for exercise in exercises],
        meta={"limit": limit, "offset": offset, "total": total},
    )


@router.get("/exercises/{exercise_id}", response_model=ExerciseDetailEnvelope)
def get_exercise(
    exercise_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> ExerciseDetailEnvelope:
    exercise = (
        db.query(Exercise)
        .filter(Exercise.id == exercise_id, Exercise.user_id == user.id)
        .one_or_none()
    )
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return ExerciseDetailEnvelope(data=_serialize_exercise(exercise))


@router.post("/exercises/{exercise_id}/attempts", response_model=ExerciseAttemptEnvelope)
def create_attempt(
    exercise_id: uuid.UUID,
    payload: ExerciseAttemptCreateRequest,
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> ExerciseAttemptEnvelope:
    exercise = (
        db.query(Exercise)
        .filter(Exercise.id == exercise_id, Exercise.user_id == user.id)
        .one_or_none()
    )
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")

    attempt = ExerciseAttempt(
        exercise_id=exercise.id,
        user_id=user.id,
        status=SubmissionStatus.submitted if payload.submit else SubmissionStatus.draft,
        answer_markdown=payload.answer_markdown,
        answer_code=payload.answer_code,
        answer_sql=payload.answer_sql,
        answer_json=payload.answer_json,
        submitted_at=(None if not payload.submit else datetime.now(timezone.utc)),
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return ExerciseAttemptEnvelope(
        data=ExerciseAttemptEnvelopeData(
            attempt=ExerciseAttemptRead.model_validate(attempt),
        )
    )


@router.post("/exercise-attempts/{attempt_id}/evaluate", response_model=ExerciseEvaluationEnvelope)
def evaluate_attempt(
    attempt_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> ExerciseEvaluationEnvelope:
    attempt = (
        db.query(ExerciseAttempt)
        .filter(ExerciseAttempt.id == attempt_id, ExerciseAttempt.user_id == user.id)
        .one_or_none()
    )
    if attempt is None:
        raise HTTPException(status_code=404, detail="Exercise attempt not found")
    if attempt.status == SubmissionStatus.draft:
        attempt.status = SubmissionStatus.submitted
        db.commit()
        db.refresh(attempt)

    evaluation = persist_evaluation(db, attempt)
    return ExerciseEvaluationEnvelope(
        data=ExerciseEvaluationRead(
            overall_score=evaluation.overall_score,
            rubricScores=evaluation.rubric_scores_json,
            strengths=evaluation.strengths_json,
            weaknesses=evaluation.weaknesses_json,
            feedbackMarkdown=evaluation.feedback_markdown,
            recommendedNextTopics=evaluation.recommended_next_topics,
            improvementActions=evaluation.improvement_actions_json,
        )
    )


@router.get("/exercise-attempts/{attempt_id}", response_model=ExerciseAttemptEnvelope)
def get_attempt(
    attempt_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> ExerciseAttemptEnvelope:
    attempt = (
        db.query(ExerciseAttempt)
        .filter(ExerciseAttempt.id == attempt_id, ExerciseAttempt.user_id == user.id)
        .one_or_none()
    )
    if attempt is None:
        raise HTTPException(status_code=404, detail="Exercise attempt not found")
    return ExerciseAttemptEnvelope(
        data=ExerciseAttemptEnvelopeData(attempt=ExerciseAttemptRead.model_validate(attempt))
    )


@router.get("/topic-mastery", response_model=TopicMasteryEnvelope)
def list_topic_mastery(
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> TopicMasteryEnvelope:
    mastery = (
        db.query(UserTopicMastery)
        .filter(UserTopicMastery.user_id == user.id)
        .order_by(UserTopicMastery.average_score.asc(), UserTopicMastery.attempts_count.desc())
        .all()
    )
    return TopicMasteryEnvelope(data=[TopicMasteryRead.model_validate(item) for item in mastery])
