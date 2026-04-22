import pytest
from sqlalchemy import inspect

from app.core.config import get_settings
from tests.db_utils import reset_public_schema
from tests.migration_utils import upgrade_to_head


@pytest.mark.integration
def test_alembic_upgrade_creates_epic1_tables(integration_engine):
    settings = get_settings()
    reset_public_schema(integration_engine)

    upgrade_to_head(settings.database_url)

    inspector = inspect(integration_engine)
    table_names = set(inspector.get_table_names())

    assert {"users", "user_profiles", "skills", "user_skills", "alembic_version"} <= table_names
