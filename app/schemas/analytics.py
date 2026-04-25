import uuid
from datetime import datetime

from app.schemas.base import ApiSchema


class AnalyticsSummary(ApiSchema):
    total_exercises_completed: int
    average_score: float | None
    streak_days: int


class AnalyticsTopic(ApiSchema):
    topic: str
    weakest_dimension: str | None = None
    mastery_score: float
    attempts_count: int
    updated_at: datetime | None = None


class AnalyticsActivity(ApiSchema):
    type: str
    entity_id: uuid.UUID
    title: str
    created_at: datetime


class AnalyticsDashboard(ApiSchema):
    summary: AnalyticsSummary
    weak_topics: list[AnalyticsTopic]
    strong_topics: list[AnalyticsTopic]
    recent_activity: list[AnalyticsActivity]


class AnalyticsDashboardEnvelope(ApiSchema):
    data: AnalyticsDashboard


class AnalyticsTopicMasteryEnvelope(ApiSchema):
    data: list[AnalyticsTopic]
