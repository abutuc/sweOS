import pytest
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.goal import Goal
from tests.migration_utils import upgrade_to_head


@pytest.mark.integration
def test_get_goals_returns_persisted_goals(
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
            Goal(
                user_id=authenticated_user.id,
                title="Move into backend role",
                description="Focus on backend depth",
                priority=2,
                status="active",
            )
        )
        db.commit()
    finally:
        db.close()

    response = integration_client.get("/api/v1/goals", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["data"][0]["title"] == "Move into backend role"


@pytest.mark.integration
def test_create_goal_persists_goal(integration_client, db_session_factory, authenticated_user, auth_headers):
    settings = get_settings()
    upgrade_to_head(settings.test_database_url)

    response = integration_client.post(
        "/api/v1/goals",
        headers=auth_headers,
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
        goal = db.query(Goal).filter(Goal.user_id == authenticated_user.id).one()
        assert goal.title == "Land AI engineer role"
        assert goal.priority == 1
    finally:
        db.close()


@pytest.mark.integration
def test_update_goal_persists_changes(
    integration_client,
    db_session_factory,
    authenticated_user,
    auth_headers,
):
    settings = get_settings()
    upgrade_to_head(settings.test_database_url)

    db: Session = db_session_factory()
    try:
        goal = Goal(
            user_id=authenticated_user.id,
            title="Land AI engineer role",
            description="Initial plan",
            priority=3,
            status="active",
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        goal_id = goal.id
    finally:
        db.close()

    response = integration_client.put(
        f"/api/v1/goals/{goal_id}",
        headers=auth_headers,
        json={
            "title": "Land senior AI engineer role",
            "description": "Tighter plan",
            "priority": 1,
            "status": "active",
        },
    )

    assert response.status_code == 200
    assert response.json()["data"]["title"] == "Land senior AI engineer role"

    db = db_session_factory()
    try:
        goal = db.query(Goal).filter(Goal.id == goal_id).one()
        assert goal.title == "Land senior AI engineer role"
        assert goal.priority == 1
    finally:
        db.close()


@pytest.mark.integration
def test_delete_goal_removes_row(
    integration_client,
    db_session_factory,
    authenticated_user,
    auth_headers,
):
    settings = get_settings()
    upgrade_to_head(settings.test_database_url)

    db: Session = db_session_factory()
    try:
        goal = Goal(
            user_id=authenticated_user.id,
            title="Land AI engineer role",
            description="Initial plan",
            priority=3,
            status="active",
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        goal_id = goal.id
    finally:
        db.close()

    response = integration_client.delete(f"/api/v1/goals/{goal_id}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {"data": {"deleted": True}}

    db = db_session_factory()
    try:
        deleted_goal = db.query(Goal).filter(Goal.id == goal_id).one_or_none()
        assert deleted_goal is None
    finally:
        db.close()
