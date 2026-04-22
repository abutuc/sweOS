import pytest
from sqlalchemy.orm import Session

from app.core.bootstrap import get_or_create_default_user
from app.core.config import get_settings
from app.models.goal import Goal
from tests.migration_utils import upgrade_to_head


@pytest.mark.integration
def test_get_goals_returns_persisted_goals(integration_client, db_session_factory):
    settings = get_settings()
    upgrade_to_head(settings.database_url)

    db: Session = db_session_factory()
    try:
        user = get_or_create_default_user(db)
        db.add(
            Goal(
                user_id=user.id,
                title="Move into backend role",
                description="Focus on backend depth",
                priority=2,
                status="active",
            )
        )
        db.commit()
    finally:
        db.close()

    response = integration_client.get("/api/v1/goals")

    assert response.status_code == 200
    assert response.json()["data"][0]["title"] == "Move into backend role"


@pytest.mark.integration
def test_create_goal_persists_goal(integration_client, db_session_factory):
    settings = get_settings()
    upgrade_to_head(settings.database_url)

    response = integration_client.post(
        "/api/v1/goals",
        json={
            "title": "Land AI engineer role",
            "description": "Build portfolio around AI systems",
            "priority": 1,
            "status": "active",
        },
    )

    assert response.status_code == 200
    assert response.json()["data"]["title"] == "Land AI engineer role"

    db: Session = db_session_factory()
    try:
        user = get_or_create_default_user(db)
        goal = db.query(Goal).filter(Goal.user_id == user.id).one()
        assert goal.title == "Land AI engineer role"
        assert goal.priority == 1
    finally:
        db.close()
