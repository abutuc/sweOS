import pytest

from app.core.config import get_settings
from tests.migration_utils import upgrade_to_head


@pytest.mark.integration
def test_cv_version_tailoring_and_feedback_flow(
    integration_client,
    authenticated_user,
    auth_headers,
):
    settings = get_settings()
    upgrade_to_head(settings.test_database_url)

    job_response = integration_client.post(
        "/api/v1/jobs",
        headers=auth_headers,
        json={
            "title": "AI Backend Engineer",
            "companyName": "Acme AI",
            "rawDescription": "Requirements: Python, FastAPI, PostgreSQL, LLM, Docker.",
            "location": "Remote",
            "workMode": "remote",
        },
    )
    assert job_response.status_code == 200
    job_id = job_response.json()["data"]["job"]["id"]
    parse_response = integration_client.post(f"/api/v1/jobs/{job_id}/parse", headers=auth_headers)
    assert parse_response.status_code == 200

    document_response = integration_client.post(
        "/api/v1/cvs",
        headers=auth_headers,
        json={"name": "Base CV", "description": "Primary structured CV"},
    )

    assert document_response.status_code == 200
    cv_document_id = document_response.json()["data"]["cvDocumentId"]

    version_response = integration_client.post(
        f"/api/v1/cvs/{cv_document_id}/versions",
        headers=auth_headers,
        json={
            "status": "base",
            "title": "Base CV - April 2026",
            "structuredContent": {
                "header": {
                    "fullName": "Integration User",
                    "email": "integration@example.com",
                    "location": "Portugal",
                },
                "summary": "Backend engineer focused on Python services.",
                "experience": [
                    {
                        "company": "Company X",
                        "role": "Software Engineer",
                        "bullets": ["Built backend APIs serving 1000 users."],
                    }
                ],
                "skills": {"languages": ["Python"], "frameworks": ["FastAPI"]},
                "education": [],
            },
        },
    )

    assert version_response.status_code == 200
    base_version_id = version_response.json()["data"]["cvVersionId"]

    tailor_response = integration_client.post(
        f"/api/v1/cvs/{cv_document_id}/tailor",
        headers=auth_headers,
        json={
            "baseVersionId": base_version_id,
            "jobId": job_id,
            "preferences": {"emphasize": ["backend", "ai"]},
        },
    )

    assert tailor_response.status_code == 200
    tailored = tailor_response.json()["data"]["cvVersion"]
    assert tailored["status"] == "tailored"
    assert "AI Backend Engineer" in tailored["title"]
    assert "Relevant keywords" in tailored["renderedMarkdown"]

    list_response = integration_client.get(f"/api/v1/cvs/{cv_document_id}/versions", headers=auth_headers)

    assert list_response.status_code == 200
    assert len(list_response.json()["data"]) == 2

    feedback_response = integration_client.post(
        f"/api/v1/cv-versions/{tailored['id']}/feedback",
        headers=auth_headers,
    )

    assert feedback_response.status_code == 200
    feedback = feedback_response.json()["data"]["feedback"]
    assert feedback["score"] > 0
    assert feedback["suggestions"]
