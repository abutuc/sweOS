from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session, require_current_user
from app.models.goal import Goal
from app.models.user import User
from app.schemas.goal import (
    GoalCreate,
    GoalDeleteEnvelope,
    GoalDeleteResult,
    GoalEnvelope,
    GoalRead,
    GoalsEnvelope,
    GoalUpdate,
)


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


@router.put("/{goal_id}", response_model=GoalEnvelope)
def update_goal(
    goal_id: str,
    payload: GoalUpdate,
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> GoalEnvelope:
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user.id).one_or_none()
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")

    for field, value in payload.model_dump(by_alias=False).items():
        setattr(goal, field, value)

    db.commit()
    db.refresh(goal)
    return GoalEnvelope(data=GoalRead.model_validate(goal))


@router.delete("/{goal_id}", response_model=GoalDeleteEnvelope)
def delete_goal(
    goal_id: str,
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> GoalDeleteEnvelope:
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user.id).one_or_none()
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")

    db.delete(goal)
    db.commit()
    return GoalDeleteEnvelope(data=GoalDeleteResult(deleted=True))
