import pytest
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.exercise_attempt import ExerciseAttempt
from app.models.exercise_evaluation import ExerciseEvaluation
from app.models.user_topic_mastery import UserTopicMastery
from tests.migration_utils import upgrade_to_head


@pytest.mark.integration
def test_generate_and_list_exercises(integration_client, db_session_factory, authenticated_user, auth_headers):
    settings = get_settings()
    upgrade_to_head(settings.database_url)

    generate_response = integration_client.post(
        "/api/v1/exercises/generate",
        headers=auth_headers,
        json={
            "type": "system_design",
            "topic": "scalability",
            "subtopic": "rate limiting",
            "difficulty": "medium",
            "timeLimitMinutes": 30,
            "includeHints": True,
            "context": {
                "targetRole": "Software Engineer II",
                "weakTopics": ["trade-off analysis"],
            },
        },
    )

    assert generate_response.status_code == 200
    assert generate_response.json()["data"]["exercise"]["topic"] == "scalability"

    list_response = integration_client.get("/api/v1/exercises", headers=auth_headers)

    assert list_response.status_code == 200
    assert list_response.json()["meta"]["total"] == 1
    assert list_response.json()["data"][0]["topic"] == "scalability"


@pytest.mark.integration
def test_create_and_evaluate_attempt_updates_mastery(
    integration_client,
    db_session_factory,
    authenticated_user,
    auth_headers,
):
    settings = get_settings()
    upgrade_to_head(settings.database_url)

    db: Session = db_session_factory()
    try:
        exercise = Exercise(
            user_id=authenticated_user.id,
            type=ExerciseType.system_design,
            topic="distributed systems",
            subtopic="rate limiting",
            difficulty=DifficultyLevel.medium,
            title="Applied System Design on Rate Limiting",
            prompt_markdown="Design a rate limiter",
            constraints_json={"timeLimitMinutes": 30},
            expected_outcomes_json=["Explains trade-offs"],
            hints_json=["Think about fairness"],
            canonical_solution_json={"summary": "Use a token bucket"},
            tags=["distributed-systems", "rate-limiting"],
        )
        db.add(exercise)
        db.commit()
        db.refresh(exercise)
        exercise_id = exercise.id
    finally:
        db.close()

    attempt_response = integration_client.post(
        f"/api/v1/exercises/{exercise_id}/attempts",
        headers=auth_headers,
        json={
            "answerMarkdown": "I would use a token bucket because it balances fairness and burst traffic.",
            "answerCode": "def rate_limit(): pass",
            "submit": True,
        },
    )

    assert attempt_response.status_code == 200
    attempt_id = attempt_response.json()["data"]["attempt"]["id"]

    evaluation_response = integration_client.post(
        f"/api/v1/exercise-attempts/{attempt_id}/evaluate",
        headers=auth_headers,
    )

    assert evaluation_response.status_code == 200
    assert evaluation_response.json()["data"]["overallScore"] > 0
    assert evaluation_response.json()["data"]["recommendedNextTopics"]

    db = db_session_factory()
    try:
        attempt = db.query(ExerciseAttempt).filter(ExerciseAttempt.id == attempt_id).one()
        evaluation = db.query(ExerciseEvaluation).filter(ExerciseEvaluation.attempt_id == attempt.id).one()
        mastery = (
            db.query(UserTopicMastery)
            .filter(
                UserTopicMastery.user_id == authenticated_user.id,
                UserTopicMastery.topic == "distributed systems",
            )
            .one()
        )
        assert attempt.status.value == "evaluated"
        assert evaluation.overall_score > 0
        assert mastery.attempts_count == 1
        assert mastery.average_score > 0
    finally:
        db.close()
