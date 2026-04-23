import uuid
from datetime import date

from pydantic import ConfigDict, Field

from app.schemas.base import ApiSchema


class GoalBase(ApiSchema):
    title: str
    description: str | None = None
    target_date: date | None = None
    horizon: str = Field(default="medium", pattern="^(short|medium|long)$")
    priority: int = Field(default=3, ge=1, le=5)
    status: str = "active"


class GoalCreate(GoalBase):
    pass


class GoalUpdate(GoalBase):
    pass


class GoalRead(GoalBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID


class GoalsEnvelope(ApiSchema):
    data: list[GoalRead]


class GoalEnvelope(ApiSchema):
    data: GoalRead


class GoalDeleteResult(ApiSchema):
    deleted: bool


class GoalDeleteEnvelope(ApiSchema):
    data: GoalDeleteResult
