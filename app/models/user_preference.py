import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    content_sources: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    notification_cadence: Mapped[str] = mapped_column(String, nullable=False, default="weekly")
    ai_assistance_level: Mapped[str] = mapped_column(String, nullable=False, default="balanced")
    privacy_settings: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    target_opportunity_filters: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", backref="preferences")
