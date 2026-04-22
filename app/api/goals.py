from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session, require_current_user
from app.models.goal import Goal
from app.models.user import User
from app.schemas.goal import GoalCreate, GoalEnvelope, GoalRead, GoalsEnvelope


router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("", response_model=GoalsEnvelope)
def get_goals(
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> GoalsEnvelope:
    goals = db.query(Goal).filter(Goal.user_id == user.id).all()
    return GoalsEnvelope(data=[GoalRead.model_validate(goal) for goal in goals])


@router.post("", response_model=GoalEnvelope)
def create_goal(
    payload: GoalCreate,
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> GoalEnvelope:
    goal = Goal(user_id=user.id, **payload.model_dump(by_alias=False))
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return GoalEnvelope(data=GoalRead.model_validate(goal))
