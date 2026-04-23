import uuid
from typing import Annotated
from decimal import Decimal

from pydantic import ConfigDict, Field, field_validator, model_validator

from app.schemas.base import ApiSchema

YearsExperience = Annotated[Decimal, Field(ge=0, max_digits=4, decimal_places=1)]
NonNegativeInt = Annotated[int, Field(ge=0)]


class ProfileBase(ApiSchema):
    headline: str | None = None
    bio: str | None = None
    years_experience: YearsExperience | None = None
    current_role: str | None = None
    stack: list[str] | None = None
    target_role: str | None = None
    target_roles: list[str] | None = None
    target_seniority: str | None = None
    preferred_industries: list[str] | None = None
    preferred_locations: list[str] | None = None
    preferred_work_modes: list[str] | None = None
    salary_expectation_min: NonNegativeInt | None = None
    salary_expectation_max: NonNegativeInt | None = None
    learning_goals: list[str] | None = None
    summary: str | None = None

    @field_validator(
        "stack",
        "target_roles",
        "preferred_industries",
        "preferred_locations",
        "preferred_work_modes",
        "learning_goals",
        mode="before",
    )
    @classmethod
    def normalize_list_fields(cls, value):
        return [] if value is None else value

    @model_validator(mode="after")
    def validate_salary_range(self):
        if (
            self.salary_expectation_min is not None
            and self.salary_expectation_max is not None
            and self.salary_expectation_min > self.salary_expectation_max
        ):
            raise ValueError("salaryExpectationMin must be less than or equal to salaryExpectationMax")
        return self


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
