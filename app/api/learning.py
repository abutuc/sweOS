from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session, require_current_user
from app.api.profile_defaults import empty_profile_for
from app.models.exercise import Exercise
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.user_topic_mastery import UserTopicMastery
from app.schemas.exercise import ExerciseSummary, TopicMasteryRead
from app.schemas.learning import LearningSummary, LearningSummaryEnvelope
from app.schemas.profile import ProfileRead


router = APIRouter(prefix="/learning", tags=["learning"])


@router.get("/summary", response_model=LearningSummaryEnvelope)
def get_learning_summary(
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> LearningSummaryEnvelope:
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).one_or_none()
    exercises = (
        db.query(Exercise)
        .filter(Exercise.user_id == user.id)
        .order_by(Exercise.created_at.desc())
        .limit(20)
        .all()
    )
    topic_mastery = (
        db.query(UserTopicMastery)
        .filter(UserTopicMastery.user_id == user.id)
        .order_by(UserTopicMastery.average_score.asc(), UserTopicMastery.attempts_count.desc())
        .all()
    )

    return LearningSummaryEnvelope(
        data=LearningSummary(
            profile=ProfileRead.model_validate(profile) if profile else empty_profile_for(user),
            exercises=[ExerciseSummary.model_validate(exercise) for exercise in exercises],
            topic_mastery=[TopicMasteryRead.model_validate(item) for item in topic_mastery],
        )
    )
