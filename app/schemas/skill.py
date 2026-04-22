import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import ConfigDict

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


class UserSkillsUpsertResult(ApiSchema):
    updated_count: int


class UserSkillsUpsertEnvelope(ApiSchema):
    data: UserSkillsUpsertResult
