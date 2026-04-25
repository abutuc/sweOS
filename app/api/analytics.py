from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies import get_db_session, require_current_user
from app.models.exercise_attempt import ExerciseAttempt
from app.models.exercise_evaluation import ExerciseEvaluation
from app.models.user import User
from app.models.user_topic_mastery import UserTopicMastery
from app.schemas.analytics import (
    AnalyticsActivity,
    AnalyticsDashboard,
    AnalyticsDashboardEnvelope,
    AnalyticsSummary,
    AnalyticsTopic,
)


router = APIRouter(prefix="/analytics", tags=["analytics"])


def _calculate_streak_days(evaluated_dates: list[date]) -> int:
    unique_dates = sorted(set(evaluated_dates), reverse=True)
    if not unique_dates:
        return 0

    streak = 1
    previous = unique_dates[0]
    for current in unique_dates[1:]:
        if (previous - current).days != 1:
            break
        streak += 1
        previous = current
    return streak


def _serialize_topic(item: UserTopicMastery) -> AnalyticsTopic:
    return AnalyticsTopic(
        topic=item.topic,
        weakest_dimension=item.weakest_dimension,
        mastery_score=round(item.average_score, 2),
        attempts_count=item.attempts_count,
    )


@router.get("/dashboard", response_model=AnalyticsDashboardEnvelope)
def get_analytics_dashboard(
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> AnalyticsDashboardEnvelope:
    completed_query = (
        db.query(ExerciseEvaluation)
        .join(ExerciseAttempt, ExerciseAttempt.id == ExerciseEvaluation.attempt_id)
        .filter(ExerciseAttempt.user_id == user.id)
    )
    completed_count = completed_query.count()
    average_score = completed_query.with_entities(func.avg(ExerciseEvaluation.overall_score)).scalar()

    evaluated_dates = [
        evaluated_at.date()
        for (evaluated_at,) in (
            db.query(ExerciseAttempt.evaluated_at)
            .filter(ExerciseAttempt.user_id == user.id, ExerciseAttempt.evaluated_at.isnot(None))
            .all()
        )
    ]
    topic_mastery = db.query(UserTopicMastery).filter(UserTopicMastery.user_id == user.id)
    weak_topics = topic_mastery.order_by(
        UserTopicMastery.average_score.asc(),
        UserTopicMastery.attempts_count.desc(),
    ).limit(5).all()
    strong_topics = topic_mastery.order_by(
        UserTopicMastery.average_score.desc(),
        UserTopicMastery.attempts_count.desc(),
    ).limit(5).all()
    recent_evaluations = (
        completed_query.options(
            joinedload(ExerciseEvaluation.attempt).joinedload(ExerciseAttempt.exercise),
        )
        .order_by(ExerciseEvaluation.created_at.desc())
        .limit(10)
        .all()
    )

    return AnalyticsDashboardEnvelope(
        data=AnalyticsDashboard(
            summary=AnalyticsSummary(
                total_exercises_completed=completed_count,
                average_score=round(float(average_score), 2) if average_score is not None else None,
                streak_days=_calculate_streak_days(evaluated_dates),
            ),
            weak_topics=[_serialize_topic(item) for item in weak_topics],
            strong_topics=[_serialize_topic(item) for item in strong_topics],
            recent_activity=[
                AnalyticsActivity(
                    type="exercise_evaluated",
                    entity_id=evaluation.attempt_id,
                    title=evaluation.attempt.exercise.title,
                    created_at=evaluation.created_at,
                )
                for evaluation in recent_evaluations
            ],
        )
    )
