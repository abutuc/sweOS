import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ExerciseType(str, enum.Enum):
    dsa = "dsa"
    system_design = "system_design"
    architecture_decision = "architecture_decision"
    database_optimization = "database_optimization"
    debugging = "debugging"
    agile_scenario = "agile_scenario"
    code_review = "code_review"


class DifficultyLevel(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class SourceType(str, enum.Enum):
    manual = "manual"
    rss = "rss"
    job_board = "job_board"
    import_ = "import"
    ai_generated = "ai_generated"


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    type: Mapped[ExerciseType] = mapped_column(
        Enum(
            ExerciseType,
            name="exercise_type",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
    )
    topic: Mapped[str] = mapped_column(String, nullable=False)
    subtopic: Mapped[str | None] = mapped_column(String, nullable=True)
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        Enum(
            DifficultyLevel,
            name="difficulty_level",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    prompt_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    constraints_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    expected_outcomes_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    hints_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    canonical_solution_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    source: Mapped[SourceType] = mapped_column(
        Enum(
            SourceType,
            name="source_type",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=SourceType.ai_generated,
    )
    created_by_ai: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    user = relationship("User", backref="generated_exercises")
