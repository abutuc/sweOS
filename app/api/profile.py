from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.core.bootstrap import get_or_create_default_user
from app.models.user_profile import UserProfile
from app.schemas.profile import ProfileEnvelope, ProfileRead


router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileEnvelope)
def get_profile(db: Session = Depends(get_db_session)) -> ProfileEnvelope:
    user = get_or_create_default_user(db)
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).one_or_none()

    if profile is None:
        return ProfileEnvelope(
            data=ProfileRead(
                user_id=user.id,
                headline=None,
                bio=None,
                years_experience=Decimal("0.0"),
                current_role=None,
                target_role=None,
                target_seniority=None,
                preferred_locations=[],
                preferred_work_modes=[],
                salary_expectation_min=None,
                salary_expectation_max=None,
                summary=None,
            )
        )

    return ProfileEnvelope(data=ProfileRead.model_validate(profile))
