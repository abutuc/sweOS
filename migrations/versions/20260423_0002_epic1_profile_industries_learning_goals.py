"""add epic1 profile industries and learning goals

Revision ID: 20260423_0002
Revises: 20260422_0001
Create Date: 2026-04-23 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260423_0002"
down_revision: Union[str, None] = "20260422_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user_profiles",
        sa.Column("preferred_industries", postgresql.ARRAY(sa.String()), nullable=True),
    )
    op.add_column(
        "user_profiles",
        sa.Column("learning_goals", postgresql.ARRAY(sa.String()), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("user_profiles", "learning_goals")
    op.drop_column("user_profiles", "preferred_industries")
