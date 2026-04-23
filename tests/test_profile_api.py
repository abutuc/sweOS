import uuid
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.dependencies import get_db_session, require_current_user
from app.main import app


class _FakeQuery:
    def filter(self, *_args, **_kwargs):
        return self

    def one_or_none(self):
        return None


class _FakeSession:
    def __init__(self):
        self.profile = None
        self.added = []
        self.committed = False

    def query(self, *_args, **_kwargs):
        session = self

        class _SessionQuery(_FakeQuery):
            def one_or_none(self_inner):
                return session.profile

        return _SessionQuery()

    def add(self, obj):
        self.added.append(obj)
        if hasattr(obj, "user_id"):
            self.profile = obj

    def commit(self):
        self.committed = True

    def close(self):
        return None


def _override_current_user(user_id: uuid.UUID):
    def _override():
        return SimpleNamespace(id=user_id)

    return _override


def test_get_profile_returns_empty_profile_shape():
    default_user_id = uuid.uuid4()
    fake_session = _FakeSession()

    def override_get_db_session():
        yield fake_session

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[require_current_user] = _override_current_user(default_user_id)

    with TestClient(app) as client:
        response = client.get("/api/v1/profile")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "userId": str(default_user_id),
            "headline": None,
            "bio": None,
            "yearsExperience": "0.0",
            "currentRole": None,
            "stack": [],
            "targetRole": None,
            "targetRoles": [],
            "targetSeniority": None,
            "preferredIndustries": [],
            "preferredLocations": [],
            "preferredWorkModes": [],
            "salaryExpectationMin": None,
            "salaryExpectationMax": None,
            "learningGoals": [],
            "summary": None,
        }
    }


def test_put_profile_creates_profile():
    default_user_id = uuid.uuid4()
    fake_session = _FakeSession()

    def override_get_db_session():
        yield fake_session

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[require_current_user] = _override_current_user(default_user_id)

    payload = {
        "headline": "Software Engineer",
        "bio": "Backend-focused engineer",
        "years_experience": "2.0",
        "current_role": "Engineer",
        "stack": ["Python", "PostgreSQL"],
        "target_role": "Backend Engineer",
        "target_roles": ["Backend Engineer", "AI Engineer"],
        "target_seniority": "mid",
        "preferred_industries": ["Developer tools"],
        "preferred_locations": ["Portugal", "Remote EU"],
        "preferred_work_modes": ["remote"],
        "salary_expectation_min": 30000,
        "salary_expectation_max": 45000,
        "learning_goals": ["System design depth"],
        "summary": "Building toward backend specialization.",
    }

    with TestClient(app) as client:
        response = client.put("/api/v1/profile", json=payload)

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"data": {"updated": True}}
    assert fake_session.committed is True
    assert fake_session.profile is not None
    assert str(fake_session.profile.user_id) == str(default_user_id)
    assert fake_session.profile.headline == payload["headline"]
    assert fake_session.profile.stack == payload["stack"]
    assert fake_session.profile.target_role == payload["target_role"]
    assert fake_session.profile.target_roles == payload["target_roles"]
    assert fake_session.profile.preferred_industries == payload["preferred_industries"]
    assert fake_session.profile.preferred_locations == payload["preferred_locations"]
    assert fake_session.profile.learning_goals == payload["learning_goals"]


def test_put_profile_rejects_invalid_salary_range():
    default_user_id = uuid.uuid4()
    fake_session = _FakeSession()

    def override_get_db_session():
        yield fake_session

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[require_current_user] = _override_current_user(default_user_id)

    with TestClient(app) as client:
        response = client.put(
            "/api/v1/profile",
            json={
                "salaryExpectationMin": 50000,
                "salaryExpectationMax": 40000,
            },
        )

    app.dependency_overrides.clear()

    assert response.status_code == 422
    assert fake_session.committed is False
