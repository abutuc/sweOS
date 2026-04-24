import uuid

import pytest
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.skill import Skill
from app.models.user_skill import UserSkill
from tests.migration_utils import upgrade_to_head


@pytest.mark.integration
def test_get_skills_catalog_returns_seeded_rows(integration_client, db_session_factory):
    settings = get_settings()
    upgrade_to_head(settings.test_database_url)

    db: Session = db_session_factory()
    try:
        db.add(
            Skill(
                id=uuid.uuid4(),
                slug="postgresql",
                name="PostgreSQL",
                category="database",
                description="Relational database",
            )
        )
        db.commit()
    finally:
        db.close()

    response = integration_client.get("/api/v1/skills/catalog")

    assert response.status_code == 200
    assert response.json()["data"][0]["slug"] == "postgresql"


@pytest.mark.integration
def test_put_and_get_my_skills_round_trip(
    integration_client,
    db_session_factory,
    authenticated_user,
    auth_headers,
):
    settings = get_settings()
    upgrade_to_head(settings.test_database_url)

    skill_id = uuid.uuid4()
    db: Session = db_session_factory()
    try:
        db.add(
            Skill(
                id=skill_id,
                slug="python",
                name="Python",
                category="language",
                description="Programming language",
            )
        )
        db.commit()
    finally:
        db.close()

    put_response = integration_client.put(
        "/api/v1/skills/me",
        headers=auth_headers,
        json={
            "skills": [
                {
                    "skillId": str(skill_id),
                    "selfAssessedLevel": "advanced",
                }
            ]
        },
    )

    assert put_response.status_code == 200
    assert put_response.json() == {"data": {"updatedCount": 1}}

    get_response = integration_client.get("/api/v1/skills/me", headers=auth_headers)

    assert get_response.status_code == 200
    assert get_response.json()["data"][0]["skillSlug"] == "python"
    assert get_response.json()["data"][0]["selfAssessedLevel"] == "advanced"

    db = db_session_factory()
    try:
        user_skill = db.query(UserSkill).filter(UserSkill.user_id == authenticated_user.id).one()
        assert user_skill.skill_id == skill_id
    finally:
        db.close()
