import pytest
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.user_preference import UserPreference
from tests.migration_utils import upgrade_to_head


@pytest.mark.integration
def test_get_preferences_returns_persisted_preferences(
    integration_client,
    db_session_factory,
    authenticated_user,
    auth_headers,
):
    settings = get_settings()
    upgrade_to_head(settings.test_database_url)

    db: Session = db_session_factory()
    try:
        db.add(
            UserPreference(
                user_id=authenticated_user.id,
                content_sources=["Hacker News", "Company blogs"],
                notification_cadence="daily",
                ai_assistance_level="balanced",
                privacy_settings={"localOnly": True},
                target_opportunity_filters={"remote": True},
            )
        )
        db.commit()
    finally:
        db.close()

    response = integration_client.get("/api/v1/preferences", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["data"]["contentSources"] == ["Hacker News", "Company blogs"]
    assert response.json()["data"]["notificationCadence"] == "daily"
    assert response.json()["data"]["privacySettings"] == {"localOnly": True}


@pytest.mark.integration
def test_put_preferences_persists_preferences(
    integration_client,
    db_session_factory,
    authenticated_user,
    auth_headers,
):
    settings = get_settings()
    upgrade_to_head(settings.test_database_url)

    response = integration_client.put(
        "/api/v1/preferences",
        headers=auth_headers,
        json={
            "contentSources": ["Hacker News", "Stack Overflow"],
            "notificationCadence": "weekly",
            "aiAssistanceLevel": "proactive",
            "privacySettings": {"shareAnalytics": False},
            "targetOpportunityFilters": {"remote": True, "salaryMin": 50000},
        },
    )

    assert response.status_code == 200
    assert response.json() == {"data": {"updated": True}}

    db: Session = db_session_factory()
    try:
        preferences = (
            db.query(UserPreference).filter(UserPreference.user_id == authenticated_user.id).one()
        )
        assert preferences.content_sources == ["Hacker News", "Stack Overflow"]
        assert preferences.notification_cadence == "weekly"
        assert preferences.ai_assistance_level == "proactive"
        assert preferences.privacy_settings == {"shareAnalytics": False}
        assert preferences.target_opportunity_filters == {"remote": True, "salaryMin": 50000}
    finally:
        db.close()
