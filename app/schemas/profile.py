import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProfileBase(BaseModel):
    headline: str | None = None
    bio: str | None = None
    years_experience: Decimal | None = Field(default=None, ge=0, max_digits=4, decimal_places=1)
    current_role: str | None = None
    target_role: str | None = None
    target_seniority: str | None = None
    preferred_locations: list[str] | None = None
    preferred_work_modes: list[str] | None = None
    salary_expectation_min: int | None = Field(default=None, ge=0)
    salary_expectation_max: int | None = Field(default=None, ge=0)
    summary: str | None = None


class ProfileUpdate(ProfileBase):
    pass


class ProfileRead(ProfileBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID


class ProfileEnvelope(BaseModel):
    data: ProfileRead


class ProfileUpdateResult(BaseModel):
    updated: bool


class ProfileUpdateEnvelope(BaseModel):
    data: ProfileUpdateResult
