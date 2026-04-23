from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session, require_current_user
from app.models.user import User
from app.models.user_preference import UserPreference
from app.schemas.preference import (
    PreferenceEnvelope,
    PreferenceRead,
    PreferenceUpdate,
    PreferenceUpdateEnvelope,
    PreferenceUpdateResult,
)


router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("", response_model=PreferenceEnvelope)
def get_preferences(
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> PreferenceEnvelope:
    preferences = db.query(UserPreference).filter(UserPreference.user_id == user.id).one_or_none()

    if preferences is None:
        return PreferenceEnvelope(
            data=PreferenceRead(
                user_id=user.id,
                content_sources=[],
                notification_cadence="weekly",
                ai_assistance_level="balanced",
                privacy_settings={},
                target_opportunity_filters={},
            )
        )

    return PreferenceEnvelope(data=PreferenceRead.model_validate(preferences))


@router.put("", response_model=PreferenceUpdateEnvelope)
def upsert_preferences(
    payload: PreferenceUpdate,
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> PreferenceUpdateEnvelope:
    preferences = db.query(UserPreference).filter(UserPreference.user_id == user.id).one_or_none()

    preference_data = payload.model_dump(by_alias=False)
    if preferences is None:
        preferences = UserPreference(user_id=user.id, **preference_data)
        db.add(preferences)
    else:
        for field, value in preference_data.items():
            setattr(preferences, field, value)

    db.commit()
    return PreferenceUpdateEnvelope(data=PreferenceUpdateResult(updated=True))
