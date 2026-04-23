import uuid
from typing import Any

from pydantic import ConfigDict, Field, field_validator

from app.schemas.base import ApiSchema


class PreferenceBase(ApiSchema):
    content_sources: list[str] = Field(default_factory=list)
    notification_cadence: str = Field(default="weekly", pattern="^(none|daily|weekly)$")
    ai_assistance_level: str = Field(default="balanced", pattern="^(minimal|balanced|proactive)$")
    privacy_settings: dict[str, Any] = Field(default_factory=dict)
    target_opportunity_filters: dict[str, Any] = Field(default_factory=dict)

    @field_validator("content_sources", mode="before")
    @classmethod
    def normalize_content_sources(cls, value):
        return [] if value is None else value

    @field_validator("privacy_settings", "target_opportunity_filters", mode="before")
    @classmethod
    def normalize_json_objects(cls, value):
        return {} if value is None else value


class PreferenceUpdate(PreferenceBase):
    pass


class PreferenceRead(PreferenceBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID


class PreferenceEnvelope(ApiSchema):
    data: PreferenceRead


class PreferenceUpdateResult(ApiSchema):
    updated: bool


class PreferenceUpdateEnvelope(ApiSchema):
    data: PreferenceUpdateResult
