import pytest
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.skill import Skill
from app.models.user_profile import UserProfile
from app.models.user_skill import ProficiencyLevel, UserSkill
from tests.migration_utils import upgrade_to_head


@pytest.mark.integration
def test_job_parse_save_and_gap_analysis_flow(
    integration_client,
    db_session_factory,
    authenticated_user,
    auth_headers,
):
    settings = get_settings()
    upgrade_to_head(settings.test_database_url)

    db: Session = db_session_factory()
    try:
        python = Skill(slug="python", name="Python", category="language")
        db.add(python)
        db.add(
            UserProfile(
                user_id=authenticated_user.id,
                headline="Backend engineer",
                stack=["Python", "PostgreSQL"],
            )
        )
        db.commit()
        db.refresh(python)
        db.add(
            UserSkill(
                user_id=authenticated_user.id,
                skill_id=python.id,
                self_assessed_level=ProficiencyLevel.advanced,
                evidence_count=2,
            )
        )
        db.commit()
    finally:
        db.close()

    create_response = integration_client.post(
        "/api/v1/jobs",
        headers=auth_headers,
        json={
            "title": "Backend Engineer - Data Platform",
            "companyName": "Acme AI",
            "rawDescription": (
                "Responsibilities\n"
                "- Build backend data platform services.\n"
                "Requirements\n"
                "- Python, PostgreSQL, Docker, distributed systems."
            ),
            "location": "Remote EU",
            "workMode": "remote",
        },
    )

    assert create_response.status_code == 200
    job_id = create_response.json()["data"]["job"]["id"]

    parse_response = integration_client.post(f"/api/v1/jobs/{job_id}/parse", headers=auth_headers)

    assert parse_response.status_code == 200
    parse_payload = parse_response.json()["data"]["parse"]
    assert "python" in parse_payload["requiredSkills"]
    assert parse_payload["responsibilities"]

    save_response = integration_client.post(
        f"/api/v1/jobs/{job_id}/save",
        headers=auth_headers,
        json={"status": "saved", "notes": "Good platform fit"},
    )

    assert save_response.status_code == 200
    user_job_id = save_response.json()["data"]["userJobId"]

    analysis_response = integration_client.post(
        f"/api/v1/user-jobs/{user_job_id}/gap-analysis",
        headers=auth_headers,
    )

    assert analysis_response.status_code == 200
    analysis = analysis_response.json()["data"]["analysis"]
    assert analysis["matchedSkills"]
    assert analysis["missingSkills"]
    assert "nextActions" in analysis["recommendation"]

    list_response = integration_client.get("/api/v1/jobs", headers=auth_headers)

    assert list_response.status_code == 200
    assert list_response.json()["data"][0]["matchScore"] is not None
