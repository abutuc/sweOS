import pytest
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.exercise import DifficultyLevel, Exercise, ExerciseType
from app.models.goal import Goal
from app.models.user_profile import UserProfile
from app.models.user_topic_mastery import UserTopicMastery
from tests.migration_utils import upgrade_to_head


@pytest.mark.integration
def test_dashboard_summary_returns_profile_and_daily_work(
    integration_client,
    db_session_factory,
    authenticated_user,
    auth_headers,
):
    settings = get_settings()
    upgrade_to_head(settings.test_database_url)

    db: Session = db_session_factory()
    try:
        db.add(
            UserProfile(
                user_id=authenticated_user.id,
                headline="Platform Engineer",
                stack=["Python", "FastAPI"],
                target_role="AI Engineer",
                target_roles=["AI Engineer"],
                learning_goals=["Practice system design"],
                summary="Preparing for AI-native backend roles.",
            )
        )
        db.add(
            Goal(
                user_id=authenticated_user.id,
                title="Complete distributed systems track",
                description="Prioritize rate limiting and consistency.",
                priority=1,
                status="active",
            )
        )
        db.add(
            Exercise(
                user_id=authenticated_user.id,
                type=ExerciseType.system_design,
                topic="distributed systems",
                difficulty=DifficultyLevel.medium,
                title="Design a rate limiter",
                prompt_markdown="Design a rate limiter for a multi-tenant API.",
                constraints_json={"timeLimitMinutes": 30},
                expected_outcomes_json=["Discusses trade-offs"],
                hints_json=["Think about token buckets"],
                tags=["distributed-systems"],
            )
        )
        db.add(
            UserTopicMastery(
                user_id=authenticated_user.id,
                topic="distributed systems",
                attempts_count=2,
                average_score=6.5,
                weakest_dimension="tradeOffReasoning",
            )
        )
        db.commit()
    finally:
        db.close()

    response = integration_client.get("/api/v1/dashboard/summary", headers=auth_headers)

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["profile"]["targetRole"] == "AI Engineer"
    assert payload["goals"][0]["title"] == "Complete distributed systems track"
    assert payload["exercises"][0]["title"] == "Design a rate limiter"
    assert payload["topicMastery"][0]["averageScore"] == 6.5
