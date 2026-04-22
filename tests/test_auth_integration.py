import pytest

from app.core.config import get_settings
from tests.migration_utils import upgrade_to_head


@pytest.mark.integration
def test_register_creates_user_and_token(integration_client):
    settings = get_settings()
    upgrade_to_head(settings.database_url)

    response = integration_client.post(
        "/api/v1/auth/register",
        json={
            "email": "andre@example.com",
            "password": "StrongPass1",
            "fullName": "Andre Butuc",
        },
    )

    assert response.status_code == 200
    assert response.json()["data"]["user"]["email"] == "andre@example.com"
    assert response.json()["data"]["token"]


@pytest.mark.integration
def test_login_returns_token_for_registered_user(integration_client):
    settings = get_settings()
    upgrade_to_head(settings.database_url)

    integration_client.post(
        "/api/v1/auth/register",
        json={
            "email": "andre@example.com",
            "password": "StrongPass1",
            "fullName": "Andre Butuc",
        },
    )

    response = integration_client.post(
        "/api/v1/auth/login",
        json={
            "email": "andre@example.com",
            "password": "StrongPass1",
        },
    )

    assert response.status_code == 200
    assert response.json()["data"]["user"]["email"] == "andre@example.com"
    assert response.json()["data"]["token"]
