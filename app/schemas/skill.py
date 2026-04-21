import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.user_skill import ProficiencyLevel


class SkillCatalogItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    name: str
    category: str
    description: str | None = None


class SkillCatalogEnvelope(BaseModel):
    data: list[SkillCatalogItem]


class UserSkillRead(BaseModel):
    skill_id: uuid.UUID
    skill_slug: str
    skill_name: str
    category: str
    self_assessed_level: ProficiencyLevel
    measured_level: ProficiencyLevel | None = None
    confidence_score: Decimal | None = None
    evidence_count: int
    last_evaluated_at: datetime | None = None


class UserSkillsEnvelope(BaseModel):
    data: list[UserSkillRead]


class UserSkillUpsertItem(BaseModel):
    skill_id: uuid.UUID
    self_assessed_level: ProficiencyLevel


class UserSkillsUpsertRequest(BaseModel):
    skills: list[UserSkillUpsertItem]


class UserSkillsUpsertResult(BaseModel):
    updated_count: int


class UserSkillsUpsertEnvelope(BaseModel):
    data: UserSkillsUpsertResult
