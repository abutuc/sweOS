import uuid
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.dependencies import get_db_session
from app.main import app


class _FakeQuery:
    def filter(self, *_args, **_kwargs):
        return self

    def one_or_none(self):
        return None


class _FakeSession:
    def query(self, *_args, **_kwargs):
        return _FakeQuery()

    def close(self):
        return None


def test_get_profile_returns_empty_profile_shape(monkeypatch):
    default_user_id = uuid.uuid4()

    def fake_get_or_create_default_user(_db):
        return SimpleNamespace(id=default_user_id)

    def override_get_db_session():
        yield _FakeSession()

    monkeypatch.setattr(
        "app.api.profile.get_or_create_default_user",
        fake_get_or_create_default_user,
    )
    app.dependency_overrides[get_db_session] = override_get_db_session

    with TestClient(app) as client:
        response = client.get("/api/v1/profile")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "user_id": str(default_user_id),
            "headline": None,
            "bio": None,
            "years_experience": "0.0",
            "current_role": None,
            "target_role": None,
            "target_seniority": None,
            "preferred_locations": [],
            "preferred_work_modes": [],
            "salary_expectation_min": None,
            "salary_expectation_max": None,
            "summary": None,
        }
    }
