import pytest
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.bootstrap import get_or_create_default_user
from app.models.user_profile import UserProfile
from tests.migration_utils import upgrade_to_head


@pytest.mark.integration
def test_get_profile_returns_persisted_profile(
    integration_client,
    db_session_factory,
):
    settings = get_settings()
    upgrade_to_head(settings.database_url)

    db: Session = db_session_factory()
    try:
        user = get_or_create_default_user(db)
        db.add(
            UserProfile(
                user_id=user.id,
                headline="Software Engineer",
                target_role="Backend Engineer",
            )
        )
        db.commit()
    finally:
        db.close()

    response = integration_client.get("/api/v1/profile")

    assert response.status_code == 200
    assert response.json()["data"]["headline"] == "Software Engineer"
    assert response.json()["data"]["targetRole"] == "Backend Engineer"


@pytest.mark.integration
def test_put_profile_persists_profile(integration_client, db_session_factory):
    settings = get_settings()
    upgrade_to_head(settings.database_url)

    response = integration_client.put(
        "/api/v1/profile",
        json={
            "headline": "Platform Engineer",
            "targetRole": "AI Engineer",
            "salaryExpectationMin": 40000,
            "salaryExpectationMax": 50000,
        },
    )

    assert response.status_code == 200
    assert response.json() == {"data": {"updated": True}}

    db: Session = db_session_factory()
    try:
        user = get_or_create_default_user(db)
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).one()
        assert profile.headline == "Platform Engineer"
        assert profile.target_role == "AI Engineer"
        assert profile.salary_expectation_min == 40000
        assert profile.salary_expectation_max == 50000
    finally:
        db.close()
