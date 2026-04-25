"""add topic mastery practice timestamp

Revision ID: 20260423_0006
Revises: 20260423_0005
Create Date: 2026-04-23 01:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260423_0006"
down_revision: Union[str, None] = "20260423_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("user_topic_mastery", sa.Column("last_practiced_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("user_topic_mastery", "last_practiced_at")
