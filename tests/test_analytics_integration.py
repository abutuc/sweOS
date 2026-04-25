from datetime import datetime, timezone

import pytest
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.exercise import DifficultyLevel, Exercise, ExerciseType
from app.models.exercise_attempt import ExerciseAttempt, SubmissionStatus
from app.models.exercise_evaluation import ExerciseEvaluation
from app.models.user_topic_mastery import UserTopicMastery
from tests.migration_utils import upgrade_to_head


@pytest.mark.integration
def test_analytics_dashboard_summarizes_progress(
    integration_client,
    db_session_factory,
    authenticated_user,
    auth_headers,
):
    settings = get_settings()
    upgrade_to_head(settings.test_database_url)

    evaluated_at = datetime(2026, 4, 25, 10, 0, tzinfo=timezone.utc)
    db: Session = db_session_factory()
    try:
        exercise = Exercise(
            user_id=authenticated_user.id,
            type=ExerciseType.system_design,
            topic="distributed systems",
            subtopic="rate limiting",
            difficulty=DifficultyLevel.medium,
            title="Design a distributed rate limiter",
            prompt_markdown="Design a multi-tenant rate limiter.",
            constraints_json={"timeLimitMinutes": 30},
            expected_outcomes_json=["Explains trade-offs"],
            hints_json=["Consider token buckets"],
            tags=["distributed-systems"],
        )
        db.add(exercise)
        db.commit()
        db.refresh(exercise)

        attempt = ExerciseAttempt(
            exercise_id=exercise.id,
            user_id=authenticated_user.id,
            status=SubmissionStatus.evaluated,
            answer_markdown="Use token buckets because they balance burst and fairness.",
            submitted_at=evaluated_at,
            evaluated_at=evaluated_at,
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)

        db.add(
            ExerciseEvaluation(
                attempt_id=attempt.id,
                overall_score=7.5,
                rubric_scores_json={"correctness": 8.0, "tradeOffReasoning": 7.0},
                strengths_json=["Clear architecture"],
                weaknesses_json=["Needs stronger capacity math"],
                feedback_markdown="Good trade-off discussion.",
                recommended_next_topics=["capacity planning"],
                improvement_actions_json=[{"action": "Add math", "why": "Capacity matters"}],
            )
        )
        db.add(
            UserTopicMastery(
                user_id=authenticated_user.id,
                topic="distributed systems",
                attempts_count=1,
                average_score=7.5,
                weakest_dimension="capacityMath",
            )
        )
        db.commit()
    finally:
        db.close()

    response = integration_client.get("/api/v1/analytics/dashboard", headers=auth_headers)

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["summary"]["totalExercisesCompleted"] == 1
    assert payload["summary"]["averageScore"] == 7.5
    assert payload["summary"]["streakDays"] == 1
    assert payload["weakTopics"][0]["topic"] == "distributed systems"
    assert payload["weakTopics"][0]["masteryScore"] == 7.5
    assert payload["strongTopics"][0]["topic"] == "distributed systems"
    assert payload["recentActivity"][0]["type"] == "exercise_evaluated"
    assert payload["recentActivity"][0]["title"] == "Design a distributed rate limiter"


@pytest.mark.integration
def test_analytics_topic_mastery_filters_by_topic(
    integration_client,
    db_session_factory,
    authenticated_user,
    auth_headers,
):
    settings = get_settings()
    upgrade_to_head(settings.test_database_url)

    db: Session = db_session_factory()
    try:
        db.add_all(
            [
                UserTopicMastery(
                    user_id=authenticated_user.id,
                    topic="distributed systems",
                    attempts_count=2,
                    average_score=5.25,
                    weakest_dimension="tradeOffReasoning",
                ),
                UserTopicMastery(
                    user_id=authenticated_user.id,
                    topic="python",
                    attempts_count=3,
                    average_score=8.1,
                    weakest_dimension="edgeCases",
                ),
            ]
        )
        db.commit()
    finally:
        db.close()

    response = integration_client.get(
        "/api/v1/analytics/topic-mastery",
        headers=auth_headers,
        params={"topic": "distributed systems"},
    )

    assert response.status_code == 200
    assert response.json()["data"] == [
        {
            "topic": "distributed systems",
            "weakestDimension": "tradeOffReasoning",
            "masteryScore": 5.25,
            "attemptsCount": 2,
            "updatedAt": response.json()["data"][0]["updatedAt"],
        }
    ]
