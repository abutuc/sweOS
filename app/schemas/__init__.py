"""API schemas package."""

from app.schemas.auth import (
    AuthEnvelope,
    AuthLoginRequest,
    AuthRegisterRequest,
    AuthResponseData,
    AuthUser,
    AuthUserEnvelope,
    AuthUserUpdateRequest,
)
from app.schemas.goal import (
    GoalCreate,
    GoalDeleteEnvelope,
    GoalDeleteResult,
    GoalEnvelope,
    GoalRead,
    GoalUpdate,
    GoalsEnvelope,
)
from app.schemas.profile import (
    ProfileEnvelope,
    ProfileRead,
    ProfileUpdate,
    ProfileUpdateEnvelope,
    ProfileUpdateResult,
)
from app.schemas.preference import (
    PreferenceEnvelope,
    PreferenceRead,
    PreferenceUpdate,
    PreferenceUpdateEnvelope,
    PreferenceUpdateResult,
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
    "AuthEnvelope",
    "AuthLoginRequest",
    "AuthRegisterRequest",
    "AuthResponseData",
    "AuthUser",
    "AuthUserEnvelope",
    "AuthUserUpdateRequest",
    "GoalCreate",
    "GoalDeleteEnvelope",
    "GoalDeleteResult",
    "GoalEnvelope",
    "GoalRead",
    "GoalUpdate",
    "GoalsEnvelope",
    "PreferenceEnvelope",
    "PreferenceRead",
    "PreferenceUpdate",
    "PreferenceUpdateEnvelope",
    "PreferenceUpdateResult",
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
