from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session, require_current_user
from app.models.user import User
from app.models.user_profile import UserProfile
from app.schemas.profile import (
    ProfileEnvelope,
    ProfileRead,
    ProfileUpdate,
    ProfileUpdateEnvelope,
    ProfileUpdateResult,
)


router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileEnvelope)
def get_profile(
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> ProfileEnvelope:
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).one_or_none()

    if profile is None:
        return ProfileEnvelope(
            data=ProfileRead(
                user_id=user.id,
                headline=None,
                bio=None,
                years_experience=Decimal("0.0"),
                current_role=None,
                stack=[],
                target_role=None,
                target_roles=[],
                target_seniority=None,
                preferred_locations=[],
                preferred_work_modes=[],
                salary_expectation_min=None,
                salary_expectation_max=None,
                summary=None,
            )
        )

    return ProfileEnvelope(data=ProfileRead.model_validate(profile))


@router.put("", response_model=ProfileUpdateEnvelope)
def upsert_profile(
    payload: ProfileUpdate,
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> ProfileUpdateEnvelope:
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).one_or_none()

    profile_data = payload.model_dump(by_alias=False)
    if profile is None:
        profile = UserProfile(user_id=user.id, **profile_data)
        db.add(profile)
    else:
        for field, value in profile_data.items():
            setattr(profile, field, value)

    db.commit()

    return ProfileUpdateEnvelope(data=ProfileUpdateResult(updated=True))
