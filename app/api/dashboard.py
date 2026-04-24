from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session, require_current_user
from app.api.profile_defaults import empty_profile_for
from app.models.exercise import Exercise
from app.models.goal import Goal
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.user_topic_mastery import UserTopicMastery
from app.schemas.dashboard import DashboardSummary, DashboardSummaryEnvelope
from app.schemas.exercise import ExerciseSummary, TopicMasteryRead
from app.schemas.goal import GoalRead
from app.schemas.profile import ProfileRead


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummaryEnvelope)
def get_dashboard_summary(
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> DashboardSummaryEnvelope:
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).one_or_none()
    goals = (
        db.query(Goal)
        .filter(Goal.user_id == user.id)
        .order_by(Goal.priority.asc(), Goal.created_at.desc())
        .limit(5)
        .all()
    )
    exercises = (
        db.query(Exercise)
        .filter(Exercise.user_id == user.id)
        .order_by(Exercise.created_at.desc())
        .limit(6)
        .all()
    )
    topic_mastery = (
        db.query(UserTopicMastery)
        .filter(UserTopicMastery.user_id == user.id)
        .order_by(UserTopicMastery.average_score.asc(), UserTopicMastery.attempts_count.desc())
        .limit(5)
        .all()
    )

    return DashboardSummaryEnvelope(
        data=DashboardSummary(
            profile=ProfileRead.model_validate(profile) if profile else empty_profile_for(user),
            goals=[GoalRead.model_validate(goal) for goal in goals],
            exercises=[ExerciseSummary.model_validate(exercise) for exercise in exercises],
            topic_mastery=[TopicMasteryRead.model_validate(item) for item in topic_mastery],
        )
    )
