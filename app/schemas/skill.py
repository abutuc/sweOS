import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import ConfigDict, model_validator

from app.models.user_skill import ProficiencyLevel
from app.schemas.base import ApiSchema


class SkillCatalogItem(ApiSchema):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    name: str
    category: str
    description: str | None = None


class SkillCatalogEnvelope(ApiSchema):
    data: list[SkillCatalogItem]


class UserSkillRead(ApiSchema):
    skill_id: uuid.UUID
    skill_slug: str
    skill_name: str
    category: str
    self_assessed_level: ProficiencyLevel
    measured_level: ProficiencyLevel | None = None
    confidence_score: Decimal | None = None
    evidence_count: int
    last_evaluated_at: datetime | None = None


class UserSkillsEnvelope(ApiSchema):
    data: list[UserSkillRead]


class UserSkillUpsertItem(ApiSchema):
    skill_id: uuid.UUID
    self_assessed_level: ProficiencyLevel


class UserSkillsUpsertRequest(ApiSchema):
    skills: list[UserSkillUpsertItem]

    @model_validator(mode="after")
    def validate_unique_skill_ids(self):
        skill_ids = [item.skill_id for item in self.skills]
        if len(skill_ids) != len(set(skill_ids)):
            raise ValueError("skills must not contain duplicate skillId values")
        return self


class UserSkillsUpsertResult(ApiSchema):
    updated_count: int


class UserSkillsUpsertEnvelope(ApiSchema):
    data: UserSkillsUpsertResult
