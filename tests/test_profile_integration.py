import pytest
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.user_profile import UserProfile
from tests.migration_utils import upgrade_to_head


@pytest.mark.integration
def test_get_profile_returns_persisted_profile(
    integration_client,
    db_session_factory,
    authenticated_user,
    auth_headers,
):
    settings = get_settings()
    upgrade_to_head(settings.database_url)

    db: Session = db_session_factory()
    try:
        db.add(
            UserProfile(
                user_id=authenticated_user.id,
                headline="Software Engineer",
                stack=["Python", "PostgreSQL"],
                target_role="Backend Engineer",
                target_roles=["Backend Engineer", "AI Engineer"],
                preferred_industries=["Developer tools"],
                learning_goals=["System design depth"],
            )
        )
        db.commit()
    finally:
        db.close()

    response = integration_client.get("/api/v1/profile", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["data"]["headline"] == "Software Engineer"
    assert response.json()["data"]["stack"] == ["Python", "PostgreSQL"]
    assert response.json()["data"]["targetRole"] == "Backend Engineer"
    assert response.json()["data"]["targetRoles"] == ["Backend Engineer", "AI Engineer"]
    assert response.json()["data"]["preferredIndustries"] == ["Developer tools"]
    assert response.json()["data"]["learningGoals"] == ["System design depth"]


@pytest.mark.integration
def test_put_profile_persists_profile(integration_client, db_session_factory, authenticated_user, auth_headers):
    settings = get_settings()
    upgrade_to_head(settings.database_url)

    response = integration_client.put(
        "/api/v1/profile",
        headers=auth_headers,
        json={
            "headline": "Platform Engineer",
            "stack": ["Python", "FastAPI"],
            "targetRole": "AI Engineer",
            "targetRoles": ["AI Engineer", "Backend Engineer"],
            "preferredIndustries": ["AI", "Developer tools"],
            "learningGoals": ["Build AI systems portfolio"],
            "salaryExpectationMin": 40000,
            "salaryExpectationMax": 50000,
        },
    )

    assert response.status_code == 200
    assert response.json() == {"data": {"updated": True}}

    db: Session = db_session_factory()
    try:
        profile = db.query(UserProfile).filter(UserProfile.user_id == authenticated_user.id).one()
        assert profile.headline == "Platform Engineer"
        assert profile.stack == ["Python", "FastAPI"]
        assert profile.target_role == "AI Engineer"
        assert profile.target_roles == ["AI Engineer", "Backend Engineer"]
        assert profile.preferred_industries == ["AI", "Developer tools"]
        assert profile.learning_goals == ["Build AI systems portfolio"]
        assert profile.salary_expectation_min == 40000
        assert profile.salary_expectation_max == 50000
    finally:
        db.close()
