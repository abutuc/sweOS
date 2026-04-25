import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api import learning as learning_api
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
    def __init__(self, profile=None, exercises=None, mastery=None):
        self.profile = profile
        self.exercises = list(exercises or [])
        self.mastery = list(mastery or [])

    def query(self, model, *_args, **_kwargs):
        if model is learning_api.UserProfile:
            return _FakeQuery([self.profile] if self.profile else [])
        if model is learning_api.Exercise:
            return _FakeQuery(self.exercises)
        if model is learning_api.UserTopicMastery:
            return _FakeQuery(self.mastery)
        return _FakeQuery([])

    def close(self):
        return None


def _override_current_user(user_id: uuid.UUID):
    def _override():
        return SimpleNamespace(id=user_id)

    return _override


def test_get_learning_summary_returns_profile_exercises_and_mastery(monkeypatch):
    user_id = uuid.uuid4()
    now = datetime(2026, 4, 24, 12, 0, tzinfo=timezone.utc)
    fake_session = _FakeSession(
        exercises=[
            SimpleNamespace(
                id=uuid.uuid4(),
                user_id=user_id,
                type=ExerciseType.system_design,
                topic="scalability",
                difficulty=DifficultyLevel.medium,
                title="Design a cache",
                created_at=now,
            )
        ],
        mastery=[
            SimpleNamespace(
                user_id=user_id,
                topic="trade-offs",
                attempts_count=2,
                average_score=6.0,
                weakest_dimension="tradeOffReasoning",
                last_practiced_at=datetime(2026, 4, 23, 12, 0, tzinfo=timezone.utc),
            )
        ],
    )

    def override_get_db_session():
        yield fake_session

    monkeypatch.setattr(learning_api, "UserProfile", _FakeProfileModel)
    monkeypatch.setattr(learning_api, "Exercise", _FakeExerciseModel)
    monkeypatch.setattr(learning_api, "UserTopicMastery", _FakeMasteryModel)
    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[require_current_user] = _override_current_user(user_id)

    with TestClient(app) as client:
        response = client.get("/api/v1/learning/summary")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["profile"]["userId"] == str(user_id)
    assert payload["exercises"][0]["title"] == "Design a cache"
    assert payload["topicMastery"][0]["topic"] == "trade-offs"
