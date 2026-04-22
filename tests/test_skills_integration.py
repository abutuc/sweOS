import uuid

import pytest
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.skill import Skill
from tests.migration_utils import upgrade_to_head


@pytest.mark.integration
def test_get_skills_catalog_returns_seeded_rows(integration_client, db_session_factory):
    settings = get_settings()
    upgrade_to_head(settings.database_url)

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
