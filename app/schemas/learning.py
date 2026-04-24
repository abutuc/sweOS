from app.schemas.base import ApiSchema
from app.schemas.exercise import ExerciseSummary, TopicMasteryRead
from app.schemas.profile import ProfileRead


class LearningSummary(ApiSchema):
    profile: ProfileRead
    exercises: list[ExerciseSummary]
    topic_mastery: list[TopicMasteryRead]


class LearningSummaryEnvelope(ApiSchema):
    data: LearningSummary
