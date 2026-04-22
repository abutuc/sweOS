import uuid
from datetime import date
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.dependencies import get_db_session
from app.main import app


class _FakeGoalQuery:
    def __init__(self, goals):
        self._goals = goals

    def filter(self, predicate):
        return _FakeGoalQuery([goal for goal in self._goals if predicate.compare(goal)])

    def all(self):
        return self._goals


class _Predicate:
    def __init__(self, evaluator):
        self._evaluator = evaluator

    def compare(self, obj):
        return self._evaluator(obj)


class _FakeColumn:
    def __init__(self, field_name: str):
        self.field_name = field_name

    def __eq__(self, other):
        return _Predicate(lambda obj: getattr(obj, self.field_name) == other)


class _FakeGoalModel:
    user_id = _FakeColumn("user_id")

    def __init__(self, user_id, **kwargs):
        self.id = uuid.uuid4()
        self.user_id = user_id
        for key, value in kwargs.items():
            setattr(self, key, value)


class _FakeGoalSession:
    def __init__(self, goals=None):
        self.goals = list(goals or [])
        self.committed = False

    def query(self, *_args, **_kwargs):
        return _FakeGoalQuery(self.goals)

    def add(self, obj):
        self.goals.append(obj)

    def commit(self):
        self.committed = True

    def refresh(self, _obj):
        return None

    def close(self):
        return None


def test_get_goals_returns_user_goals(monkeypatch):
    user_id = uuid.uuid4()
    fake_session = _FakeGoalSession(
        [
            SimpleNamespace(
                id=uuid.uuid4(),
                user_id=user_id,
                title="Become backend-focused",
                description="Shift practice toward backend topics",
                target_date=date(2026, 6, 1),
                priority=2,
                status="active",
            )
        ]
    )

    def fake_get_or_create_default_user(_db):
        return SimpleNamespace(id=user_id)

    def override_get_db_session():
        yield fake_session

    monkeypatch.setattr("app.api.goals.get_or_create_default_user", fake_get_or_create_default_user)
    monkeypatch.setattr("app.api.goals.Goal", _FakeGoalModel)
    app.dependency_overrides[get_db_session] = override_get_db_session

    with TestClient(app) as client:
        response = client.get("/api/v1/goals")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["data"][0]["title"] == "Become backend-focused"


def test_create_goal_persists_goal(monkeypatch):
    user_id = uuid.uuid4()
    fake_session = _FakeGoalSession()

    def fake_get_or_create_default_user(_db):
        return SimpleNamespace(id=user_id)

    def override_get_db_session():
        yield fake_session

    monkeypatch.setattr("app.api.goals.get_or_create_default_user", fake_get_or_create_default_user)
    monkeypatch.setattr("app.api.goals.Goal", _FakeGoalModel)
    app.dependency_overrides[get_db_session] = override_get_db_session

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/goals",
            json={
                "title": "Land backend role",
                "description": "Strengthen backend profile",
                "targetDate": "2026-08-01",
                "priority": 2,
                "status": "active",
            },
        )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["data"]["title"] == "Land backend role"
    assert response.json()["data"]["userId"] == str(user_id)
    assert fake_session.committed is True


def test_create_goal_rejects_invalid_priority(monkeypatch):
    user_id = uuid.uuid4()
    fake_session = _FakeGoalSession()

    def fake_get_or_create_default_user(_db):
        return SimpleNamespace(id=user_id)

    def override_get_db_session():
        yield fake_session

    monkeypatch.setattr("app.api.goals.get_or_create_default_user", fake_get_or_create_default_user)
    monkeypatch.setattr("app.api.goals.Goal", _FakeGoalModel)
    app.dependency_overrides[get_db_session] = override_get_db_session

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/goals",
            json={
                "title": "Stretch goal",
                "priority": 7,
                "status": "active",
            },
        )

    app.dependency_overrides.clear()

    assert response.status_code == 422
    assert fake_session.committed is False
