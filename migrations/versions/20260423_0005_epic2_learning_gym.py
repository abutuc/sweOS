"""add epic2 learning gym tables

Revision ID: 20260423_0005
Revises: 20260423_0004
Create Date: 2026-04-23 00:30:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260423_0005"
down_revision: Union[str, None] = "20260423_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


exercise_type_enum = postgresql.ENUM(
    "dsa",
    "system_design",
    "architecture_decision",
    "database_optimization",
    "debugging",
    "agile_scenario",
    "code_review",
    name="exercise_type",
)
difficulty_level_enum = postgresql.ENUM("easy", "medium", "hard", name="difficulty_level")
submission_status_enum = postgresql.ENUM(
    "draft",
    "submitted",
    "evaluated",
    "failed_evaluation",
    name="submission_status",
)
source_type_enum = postgresql.ENUM(
    "manual",
    "rss",
    "job_board",
    "import",
    "ai_generated",
    name="source_type",
)


def upgrade() -> None:
    bind = op.get_bind()
    exercise_type_enum.create(bind, checkfirst=True)
    difficulty_level_enum.create(bind, checkfirst=True)
    submission_status_enum.create(bind, checkfirst=True)
    source_type_enum.create(bind, checkfirst=True)

    op.create_table(
        "exercises",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("type", exercise_type_enum, nullable=False),
        sa.Column("topic", sa.String(), nullable=False),
        sa.Column("subtopic", sa.String(), nullable=True),
        sa.Column("difficulty", difficulty_level_enum, nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("prompt_markdown", sa.Text(), nullable=False),
        sa.Column(
            "constraints_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "expected_outcomes_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "hints_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "canonical_solution_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("source", source_type_enum, nullable=False, server_default="ai_generated"),
        sa.Column("created_by_ai", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "exercise_attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("exercise_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", submission_status_enum, nullable=False, server_default="draft"),
        sa.Column("answer_markdown", sa.Text(), nullable=True),
        sa.Column("answer_code", sa.Text(), nullable=True),
        sa.Column("answer_sql", sa.Text(), nullable=True),
        sa.Column(
            "answer_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "exercise_evaluations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("attempt_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("overall_score", sa.Float(), nullable=False),
        sa.Column(
            "rubric_scores_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "strengths_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "weaknesses_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("feedback_markdown", sa.Text(), nullable=False),
        sa.Column(
            "recommended_next_topics",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "improvement_actions_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("evaluator_type", sa.String(), nullable=False, server_default="system"),
        sa.Column("prompt_version", sa.String(), nullable=True),
        sa.Column("model_name", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["attempt_id"], ["exercise_attempts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "user_topic_mastery",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("topic", sa.String(), nullable=False),
        sa.Column("attempts_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("average_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("weakest_dimension", sa.String(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "topic", name="uq_user_topic_mastery_user_id_topic"),
    )

    op.create_index("idx_exercises_type_topic_difficulty", "exercises", ["type", "topic", "difficulty"])
    op.create_index("idx_attempts_user_exercise", "exercise_attempts", ["user_id", "exercise_id"])
    op.create_index("idx_user_topic_mastery_user_id", "user_topic_mastery", ["user_id"])


def downgrade() -> None:
    op.drop_index("idx_user_topic_mastery_user_id", table_name="user_topic_mastery")
    op.drop_index("idx_attempts_user_exercise", table_name="exercise_attempts")
    op.drop_index("idx_exercises_type_topic_difficulty", table_name="exercises")
    op.drop_table("user_topic_mastery")
    op.drop_table("exercise_evaluations")
    op.drop_table("exercise_attempts")
    op.drop_table("exercises")

    bind = op.get_bind()
    source_type_enum.drop(bind, checkfirst=True)
    submission_status_enum.drop(bind, checkfirst=True)
    difficulty_level_enum.drop(bind, checkfirst=True)
    exercise_type_enum.drop(bind, checkfirst=True)
