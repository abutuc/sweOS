"""add epic1 goal horizon

Revision ID: 20260423_0003
Revises: 20260423_0002
Create Date: 2026-04-23 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260423_0003"
down_revision: Union[str, None] = "20260423_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "goals",
        sa.Column("horizon", sa.String(), nullable=False, server_default="medium"),
    )
    op.alter_column("goals", "horizon", server_default=None)


def downgrade() -> None:
    op.drop_column("goals", "horizon")
