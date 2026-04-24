from alembic import command
from alembic.config import Config


def build_alembic_config(database_url: str) -> Config:
    config = Config("alembic.ini")
    config.attributes["database_url"] = database_url
    return config


def upgrade_to_head(database_url: str) -> None:
    command.upgrade(build_alembic_config(database_url), "head")


def downgrade_to_base(database_url: str) -> None:
    command.downgrade(build_alembic_config(database_url), "base")
