import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ExerciseEvaluation(Base):
    __tablename__ = "exercise_evaluations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exercise_attempts.id", ondelete="CASCADE"),
        nullable=False,
    )
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    rubric_scores_json: Mapped[dict[str, float]] = mapped_column(JSONB, nullable=False, default=dict)
    strengths_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    weaknesses_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    feedback_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_next_topics: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    improvement_actions_json: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )
    evaluator_type: Mapped[str] = mapped_column(String, nullable=False, default="system")
    prompt_version: Mapped[str | None] = mapped_column(String, nullable=True)
    model_name: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    attempt = relationship("ExerciseAttempt", backref="evaluations")
