"""API schemas package."""

from app.schemas.profile import (
    ProfileEnvelope,
    ProfileRead,
    ProfileUpdate,
    ProfileUpdateEnvelope,
    ProfileUpdateResult,
)
from app.schemas.skill import (
    SkillCatalogEnvelope,
    SkillCatalogItem,
    UserSkillRead,
    UserSkillsEnvelope,
    UserSkillsUpsertEnvelope,
    UserSkillsUpsertRequest,
    UserSkillsUpsertResult,
)

__all__ = [
    "ProfileEnvelope",
    "ProfileRead",
    "ProfileUpdate",
    "ProfileUpdateEnvelope",
    "ProfileUpdateResult",
    "SkillCatalogEnvelope",
    "SkillCatalogItem",
    "UserSkillRead",
    "UserSkillsEnvelope",
    "UserSkillsUpsertEnvelope",
    "UserSkillsUpsertRequest",
    "UserSkillsUpsertResult",
]
