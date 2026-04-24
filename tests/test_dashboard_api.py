import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api import dashboard as dashboard_api
from app.api.dependencies import get_db_session, require_current_user
from app.main import app
from app.models.exercise import DifficultyLevel, ExerciseType


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

    def asc(self):
        return self

    def desc(self):
        return self


class _FakeProfileModel:
    user_id = _FakeColumn("user_id")


class _FakeGoalModel:
    user_id = _FakeColumn("user_id")
    priority = _FakeColumn("priority")
    created_at = _FakeColumn("created_at")


class _FakeExerciseModel:
    user_id = _FakeColumn("user_id")
    created_at = _FakeColumn("created_at")


class _FakeMasteryModel:
    user_id = _FakeColumn("user_id")
    average_score = _FakeColumn("average_score")
    attempts_count = _FakeColumn("attempts_count")


class _FakeQuery:
    def __init__(self, items):
        self._items = list(items)
        self._limit = None

    def filter(self, *predicates):
        return _FakeQuery(
            [item for item in self._items if all(predicate.compare(item) for predicate in predicates)]
        )

    def order_by(self, *_args):
        return self

    def limit(self, value):
        self._limit = value
        return self

    def all(self):
        return self._items[: self._limit] if self._limit is not None else self._items

    def one_or_none(self):
        return self._items[0] if self._items else None


class _FakeSession:
    def __init__(self, profile=None, goals=None, exercises=None, mastery=None):
        self.profile = profile
        self.goals = list(goals or [])
        self.exercises = list(exercises or [])
        self.mastery = list(mastery or [])

    def query(self, model, *_args, **_kwargs):
        if model is dashboard_api.UserProfile:
            return _FakeQuery([self.profile] if self.profile else [])
        if model is dashboard_api.Goal:
            return _FakeQuery(self.goals)
        if model is dashboard_api.Exercise:
            return _FakeQuery(self.exercises)
        if model is dashboard_api.UserTopicMastery:
            return _FakeQuery(self.mastery)
        return _FakeQuery([])

    def close(self):
        return None


def _override_current_user(user_id: uuid.UUID):
    def _override():
        return SimpleNamespace(id=user_id)

    return _override


def test_get_dashboard_summary_returns_daily_payload(monkeypatch):
    user_id = uuid.uuid4()
    now = datetime(2026, 4, 24, 10, 0, tzinfo=timezone.utc)
    fake_session = _FakeSession(
        profile=SimpleNamespace(
            user_id=user_id,
            headline="Backend engineer",
            bio=None,
            years_experience="2.0",
            current_role="Engineer",
            stack=["Python"],
            target_role="Backend Engineer",
            target_roles=["Backend Engineer"],
            target_seniority="mid",
            preferred_industries=[],
            preferred_locations=[],
            preferred_work_modes=[],
            salary_expectation_min=None,
            salary_expectation_max=None,
            learning_goals=[],
            summary="Backend focus",
        ),
        goals=[
            SimpleNamespace(
                id=uuid.uuid4(),
                user_id=user_id,
                title="Land backend role",
                description=None,
                target_date=None,
                horizon="medium",
                priority=2,
                status="active",
                created_at=now,
            )
        ],
        exercises=[
            SimpleNamespace(
                id=uuid.uuid4(),
                user_id=user_id,
                type=ExerciseType.system_design,
                topic="scalability",
                difficulty=DifficultyLevel.medium,
                title="Rate limiter",
                created_at=now,
            )
        ],
        mastery=[
            SimpleNamespace(
                user_id=user_id,
                topic="distributed systems",
                attempts_count=1,
                average_score=5.5,
                weakest_dimension="tradeOffReasoning",
            )
        ],
    )

    def override_get_db_session():
        yield fake_session

    monkeypatch.setattr(dashboard_api, "UserProfile", _FakeProfileModel)
    monkeypatch.setattr(dashboard_api, "Goal", _FakeGoalModel)
    monkeypatch.setattr(dashboard_api, "Exercise", _FakeExerciseModel)
    monkeypatch.setattr(dashboard_api, "UserTopicMastery", _FakeMasteryModel)
    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[require_current_user] = _override_current_user(user_id)

    with TestClient(app) as client:
        response = client.get("/api/v1/dashboard/summary")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["data"]["profile"]["targetRole"] == "Backend Engineer"
    assert response.json()["data"]["goals"][0]["title"] == "Land backend role"
    assert response.json()["data"]["exercises"][0]["topic"] == "scalability"
    assert response.json()["data"]["topicMastery"][0]["topic"] == "distributed systems"
