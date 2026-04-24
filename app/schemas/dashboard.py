from app.schemas.base import ApiSchema
from app.schemas.exercise import ExerciseSummary, TopicMasteryRead
from app.schemas.goal import GoalRead
from app.schemas.profile import ProfileRead


class DashboardSummary(ApiSchema):
    profile: ProfileRead
    goals: list[GoalRead]
    exercises: list[ExerciseSummary]
    topic_mastery: list[TopicMasteryRead]


class DashboardSummaryEnvelope(ApiSchema):
    data: DashboardSummary
