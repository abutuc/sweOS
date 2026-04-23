import uuid
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.dependencies import get_db_session, require_current_user
from app.main import app


class _FakeQuery:
    def __init__(self, preference):
        self._preference = preference

    def filter(self, *_args, **_kwargs):
        return self

    def one_or_none(self):
        return self._preference


class _FakeSession:
    def __init__(self):
        self.preference = None
        self.committed = False

    def query(self, *_args, **_kwargs):
        return _FakeQuery(self.preference)

    def add(self, obj):
        self.preference = obj

    def commit(self):
        self.committed = True

    def close(self):
        return None


def _override_current_user(user_id: uuid.UUID):
    def _override():
        return SimpleNamespace(id=user_id)

    return _override


def test_get_preferences_returns_default_shape():
    user_id = uuid.uuid4()
    fake_session = _FakeSession()

    def override_get_db_session():
        yield fake_session

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[require_current_user] = _override_current_user(user_id)

    with TestClient(app) as client:
        response = client.get("/api/v1/preferences")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "userId": str(user_id),
            "contentSources": [],
            "notificationCadence": "weekly",
            "aiAssistanceLevel": "balanced",
            "privacySettings": {},
            "targetOpportunityFilters": {},
        }
    }


def test_put_preferences_creates_preferences():
    user_id = uuid.uuid4()
    fake_session = _FakeSession()

    def override_get_db_session():
        yield fake_session

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[require_current_user] = _override_current_user(user_id)

    with TestClient(app) as client:
        response = client.put(
            "/api/v1/preferences",
            json={
                "contentSources": ["Hacker News", "Company blogs"],
                "notificationCadence": "daily",
                "aiAssistanceLevel": "proactive",
                "privacySettings": {"localOnly": True},
                "targetOpportunityFilters": {"remote": True, "locations": ["Portugal"]},
            },
        )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"data": {"updated": True}}
    assert fake_session.committed is True
    assert fake_session.preference is not None
    assert str(fake_session.preference.user_id) == str(user_id)
    assert fake_session.preference.content_sources == ["Hacker News", "Company blogs"]
    assert fake_session.preference.notification_cadence == "daily"
    assert fake_session.preference.ai_assistance_level == "proactive"


def test_put_preferences_rejects_invalid_cadence():
    user_id = uuid.uuid4()
    fake_session = _FakeSession()

    def override_get_db_session():
        yield fake_session

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[require_current_user] = _override_current_user(user_id)

    with TestClient(app) as client:
        response = client.put(
            "/api/v1/preferences",
            json={
                "notificationCadence": "hourly",
            },
        )

    app.dependency_overrides.clear()

    assert response.status_code == 422
    assert fake_session.committed is False
