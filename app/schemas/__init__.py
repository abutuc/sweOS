"""API schemas package."""

from app.schemas.goal import GoalCreate, GoalEnvelope, GoalRead, GoalsEnvelope
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
    "GoalCreate",
    "GoalEnvelope",
    "GoalRead",
    "GoalsEnvelope",
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
