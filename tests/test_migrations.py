import pytest
from sqlalchemy import inspect

from app.core.config import get_settings
from tests.db_utils import is_database_available, reset_public_schema
from tests.migration_utils import downgrade_to_base, upgrade_to_head


@pytest.mark.integration
def test_alembic_upgrade_creates_epic1_tables(integration_engine):
    settings = get_settings()
    if not is_database_available(integration_engine):
        pytest.skip("Postgres is not reachable at the configured database URL")
    reset_public_schema(integration_engine)

    upgrade_to_head(settings.test_database_url)

    inspector = inspect(integration_engine)
    table_names = set(inspector.get_table_names())

    assert {
        "users",
        "user_profiles",
        "skills",
        "user_skills",
        "goals",
        "user_preferences",
        "exercises",
        "exercise_attempts",
        "exercise_evaluations",
        "user_topic_mastery",
        "alembic_version",
    } <= table_names


@pytest.mark.integration
def test_alembic_downgrade_removes_epic1_tables(integration_engine):
    settings = get_settings()
    if not is_database_available(integration_engine):
        pytest.skip("Postgres is not reachable at the configured database URL")
    reset_public_schema(integration_engine)

    upgrade_to_head(settings.test_database_url)
    downgrade_to_base(settings.test_database_url)

    inspector = inspect(integration_engine)
    table_names = set(inspector.get_table_names())

    assert "alembic_version" in table_names
    assert "users" not in table_names
    assert "user_profiles" not in table_names
    assert "skills" not in table_names
    assert "user_skills" not in table_names
    assert "goals" not in table_names
    assert "user_preferences" not in table_names
    assert "exercises" not in table_names
    assert "exercise_attempts" not in table_names
    assert "exercise_evaluations" not in table_names
    assert "user_topic_mastery" not in table_names
