import uuid
from typing import Annotated
from decimal import Decimal

from pydantic import ConfigDict, Field

from app.schemas.base import ApiSchema


class ProfileBase(ApiSchema):
    headline: str | None = None
    bio: str | None = None
    years_experience: Annotated[
        Decimal | None,
        Field(default=None, ge=0, max_digits=4, decimal_places=1),
    ] = None
    current_role: str | None = None
    target_role: str | None = None
    target_seniority: str | None = None
    preferred_locations: list[str] | None = None
    preferred_work_modes: list[str] | None = None
    salary_expectation_min: Annotated[int | None, Field(default=None, ge=0)] = None
    salary_expectation_max: Annotated[int | None, Field(default=None, ge=0)] = None
    summary: str | None = None


class ProfileUpdate(ProfileBase):
    pass


class ProfileRead(ProfileBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID


class ProfileEnvelope(ApiSchema):
    data: ProfileRead


class ProfileUpdateResult(ApiSchema):
    updated: bool


class ProfileUpdateEnvelope(ApiSchema):
    data: ProfileUpdateResult
