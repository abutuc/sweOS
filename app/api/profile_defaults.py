from decimal import Decimal

from app.models.user import User
from app.schemas.profile import ProfileRead


def empty_profile_for(user: User) -> ProfileRead:
    return ProfileRead(
        user_id=user.id,
        headline=None,
        bio=None,
        years_experience=Decimal("0.0"),
        current_role=None,
        stack=[],
        target_role=None,
        target_roles=[],
        target_seniority=None,
        preferred_industries=[],
        preferred_locations=[],
        preferred_work_modes=[],
        salary_expectation_min=None,
        salary_expectation_max=None,
        learning_goals=[],
        summary=None,
    )
