import uuid
from datetime import datetime
from typing import Any

from pydantic import ConfigDict, Field

from app.models.exercise import DifficultyLevel, ExerciseType
from app.models.exercise_attempt import SubmissionStatus
from app.schemas.base import ApiSchema


class ExerciseGenerationContext(ApiSchema):
    target_role: str | None = None
    weak_topics: list[str] = Field(default_factory=list)


class ExerciseGenerateRequest(ApiSchema):
    type: ExerciseType
    topic: str
    subtopic: str | None = None
    difficulty: DifficultyLevel
    time_limit_minutes: int = Field(default=30, ge=5, le=120)
    include_hints: bool = True
    context: ExerciseGenerationContext = Field(default_factory=ExerciseGenerationContext)


class ExerciseSummary(ApiSchema):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: ExerciseType
    topic: str
    difficulty: DifficultyLevel
    title: str
    created_at: datetime


class ExerciseRead(ApiSchema):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: ExerciseType
    topic: str
    subtopic: str | None = None
    difficulty: DifficultyLevel
    title: str
    prompt_markdown: str
    constraints_json: dict[str, Any] = Field(alias="constraints")
    expected_outcomes_json: list[str] = Field(alias="expectedOutcomes")
    hints_json: list[str] = Field(alias="hints")
    tags: list[str]
    created_at: datetime | None = None


class ExerciseEnvelopeData(ApiSchema):
    exercise: ExerciseRead


class ExerciseGenerateEnvelope(ApiSchema):
    data: ExerciseEnvelopeData


class ExerciseListEnvelope(ApiSchema):
    data: list[ExerciseSummary]
    meta: dict[str, int]


class ExerciseDetailEnvelope(ApiSchema):
    data: ExerciseRead


class ExerciseAttemptCreateRequest(ApiSchema):
    answer_markdown: str | None = None
    answer_code: str | None = None
    answer_sql: str | None = None
    answer_json: dict[str, Any] = Field(default_factory=dict)
    submit: bool = True


class ExerciseAttemptRead(ApiSchema):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    exercise_id: uuid.UUID
    status: SubmissionStatus
    answer_markdown: str | None = None
    answer_code: str | None = None
    answer_sql: str | None = None
    answer_json: dict[str, Any]
    submitted_at: datetime | None = None
    evaluated_at: datetime | None = None


class ExerciseAttemptEnvelopeData(ApiSchema):
    attempt: ExerciseAttemptRead


class ExerciseAttemptEnvelope(ApiSchema):
    data: ExerciseAttemptEnvelopeData


class ExerciseEvaluationRead(ApiSchema):
    model_config = ConfigDict(from_attributes=True)

    overall_score: float
    rubric_scores_json: dict[str, float] = Field(alias="rubricScores")
    strengths_json: list[str] = Field(alias="strengths")
    weaknesses_json: list[str] = Field(alias="weaknesses")
    feedback_markdown: str = Field(alias="feedbackMarkdown")
    recommended_next_topics: list[str] = Field(alias="recommendedNextTopics")
    improvement_actions_json: list[dict[str, Any]] = Field(alias="improvementActions")


class ExerciseEvaluationEnvelope(ApiSchema):
    data: ExerciseEvaluationRead


class TopicMasteryRead(ApiSchema):
    model_config = ConfigDict(from_attributes=True)

    topic: str
    attempts_count: int
    average_score: float
    weakest_dimension: str | None = None


class TopicMasteryEnvelope(ApiSchema):
    data: list[TopicMasteryRead]
