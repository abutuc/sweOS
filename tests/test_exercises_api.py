import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api import exercises as exercises_api
from app.api.dependencies import get_db_session, require_current_user
from app.main import app
from app.models.exercise import DifficultyLevel, ExerciseType
from app.models.exercise_attempt import SubmissionStatus


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


class _FakeExerciseModel:
    id = _FakeColumn("id")
    user_id = _FakeColumn("user_id")
    type = _FakeColumn("type")
    topic = _FakeColumn("topic")
    difficulty = _FakeColumn("difficulty")
    created_at = _FakeColumn("created_at")


class _FakeAttemptModel:
    id = _FakeColumn("id")
    user_id = _FakeColumn("user_id")


class _FakeTopicMasteryModel:
    user_id = _FakeColumn("user_id")
    average_score = _FakeColumn("average_score")
    attempts_count = _FakeColumn("attempts_count")


class _FakeQuery:
    def __init__(self, items):
        self._items = list(items)
        self._offset = 0
        self._limit = None

    def filter(self, *predicates):
        return _FakeQuery(
            [item for item in self._items if all(predicate.compare(item) for predicate in predicates)]
        )

    def order_by(self, *_args, **_kwargs):
        return self

    def offset(self, value):
        self._offset = value
        return self

    def limit(self, value):
        self._limit = value
        return self

    def count(self):
        return len(self._items)

    def all(self):
        items = self._items[self._offset :]
        if self._limit is not None:
            items = items[: self._limit]
        return items

    def one_or_none(self):
        return self._items[0] if self._items else None


class _FakeSession:
    def __init__(self, exercises=None, attempts=None, mastery=None):
        self.exercises = list(exercises or [])
        self.attempts = list(attempts or [])
        self.mastery = list(mastery or [])
        self.committed = False

    def query(self, model, *_args, **_kwargs):
        if model is exercises_api.Exercise:
            return _FakeQuery(self.exercises)
        if model is exercises_api.ExerciseAttempt:
            return _FakeQuery(self.attempts)
        if model is exercises_api.UserTopicMastery:
            return _FakeQuery(self.mastery)
        return _FakeQuery([])

    def add(self, obj):
        if hasattr(obj, "exercise_id"):
            self.attempts.append(obj)
        else:
            self.exercises.append(obj)

    def commit(self):
        self.committed = True

    def refresh(self, _obj):
        return None

    def close(self):
        return None


def _override_current_user(user_id: uuid.UUID):
    def _override():
        return SimpleNamespace(id=user_id)

    return _override


def test_generate_exercise_returns_generated_exercise(monkeypatch):
    user_id = uuid.uuid4()
    exercise_id = uuid.uuid4()
    fake_session = _FakeSession()

    def override_get_db_session():
        yield fake_session

    generated_exercise = SimpleNamespace(
        id=exercise_id,
        user_id=user_id,
        type=ExerciseType.system_design,
        topic="scalability",
        subtopic="rate limiting",
        difficulty=DifficultyLevel.medium,
        title="Applied System Design on Rate Limiting",
        prompt_markdown="Design a rate limiter",
        constraints_json={"timeLimitMinutes": 30},
        expected_outcomes_json=["Explains trade-offs"],
        hints_json=["Think about fairness"],
        tags=["scalability", "rate-limiting"],
        created_at=datetime(2026, 4, 23, 12, 0, tzinfo=timezone.utc),
    )

    monkeypatch.setattr(exercises_api, "create_exercise_from_request", lambda *_args, **_kwargs: generated_exercise)
    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[require_current_user] = _override_current_user(user_id)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/exercises/generate",
            json={
                "type": "system_design",
                "topic": "scalability",
                "subtopic": "rate limiting",
                "difficulty": "medium",
                "timeLimitMinutes": 30,
                "includeHints": True,
                "context": {"targetRole": "Software Engineer II", "weakTopics": ["trade-off analysis"]},
            },
        )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["data"]["exercise"]["id"] == str(exercise_id)


def test_list_exercises_returns_user_exercises(monkeypatch):
    user_id = uuid.uuid4()
    fake_session = _FakeSession(
        exercises=[
            SimpleNamespace(
                id=uuid.uuid4(),
                user_id=user_id,
                type=ExerciseType.dsa,
                topic="arrays",
                difficulty=DifficultyLevel.easy,
                title="Two Sum Variant",
                created_at=datetime(2026, 4, 23, 12, 0, tzinfo=timezone.utc),
            )
        ]
    )

    def override_get_db_session():
        yield fake_session

    monkeypatch.setattr(exercises_api, "Exercise", _FakeExerciseModel)
    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[require_current_user] = _override_current_user(user_id)

    with TestClient(app) as client:
        response = client.get("/api/v1/exercises")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["data"][0]["title"] == "Two Sum Variant"
    assert response.json()["meta"]["total"] == 1


def test_get_exercise_returns_full_exercise(monkeypatch):
    user_id = uuid.uuid4()
    exercise_id = uuid.uuid4()
    fake_session = _FakeSession(
        exercises=[
            SimpleNamespace(
                id=exercise_id,
                user_id=user_id,
                type=ExerciseType.dsa,
                topic="arrays",
                subtopic="two-pointers",
                difficulty=DifficultyLevel.easy,
                title="Two Sum Variant",
                prompt_markdown="Solve it",
                constraints_json={"timeLimitMinutes": 20},
                expected_outcomes_json=["Handles edge cases"],
                hints_json=["Sort before searching"],
                tags=["arrays", "hashmap"],
                created_at=datetime(2026, 4, 23, 12, 0, tzinfo=timezone.utc),
            )
        ]
    )

    def override_get_db_session():
        yield fake_session

    monkeypatch.setattr(exercises_api, "Exercise", _FakeExerciseModel)
    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[require_current_user] = _override_current_user(user_id)

    with TestClient(app) as client:
        response = client.get(f"/api/v1/exercises/{exercise_id}")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["data"]["subtopic"] == "two-pointers"


def test_create_attempt_persists_attempt(monkeypatch):
    user_id = uuid.uuid4()
    exercise_id = uuid.uuid4()
    fake_session = _FakeSession(
        exercises=[
            SimpleNamespace(
                id=exercise_id,
                user_id=user_id,
            )
        ]
    )

    def override_get_db_session():
        yield fake_session

    class _WritableAttemptModel(_FakeAttemptModel):
        def __init__(self, **kwargs):
            self.id = uuid.uuid4()
            for key, value in kwargs.items():
                setattr(self, key, value)

    monkeypatch.setattr(exercises_api, "Exercise", _FakeExerciseModel)
    monkeypatch.setattr(exercises_api, "ExerciseAttempt", _WritableAttemptModel)
    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[require_current_user] = _override_current_user(user_id)

    with TestClient(app) as client:
        response = client.post(
            f"/api/v1/exercises/{exercise_id}/attempts",
            json={"answerMarkdown": "My reasoning", "submit": True},
        )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["data"]["attempt"]["status"] == "submitted"
    assert fake_session.committed is True


def test_evaluate_attempt_returns_feedback(monkeypatch):
    user_id = uuid.uuid4()
    attempt_id = uuid.uuid4()
    fake_session = _FakeSession(
        attempts=[
            SimpleNamespace(
                id=attempt_id,
                user_id=user_id,
                status=SubmissionStatus.submitted,
            )
        ]
    )

    def override_get_db_session():
        yield fake_session

    monkeypatch.setattr(exercises_api, "ExerciseAttempt", _FakeAttemptModel)
    monkeypatch.setattr(
        exercises_api,
        "persist_evaluation",
        lambda *_args, **_kwargs: SimpleNamespace(
            overall_score=7.4,
            rubric_scores_json={"correctness": 8},
            strengths_json=["Good structure"],
            weaknesses_json=["Need stronger trade-offs"],
            feedback_markdown="Strong answer overall.",
            recommended_next_topics=["trade-off analysis"],
            improvement_actions_json=[{"action": "Explain trade-offs", "why": "Low score"}],
        ),
    )
    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[require_current_user] = _override_current_user(user_id)

    with TestClient(app) as client:
        response = client.post(f"/api/v1/exercise-attempts/{attempt_id}/evaluate")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["data"]["overallScore"] == 7.4
    assert response.json()["data"]["recommendedNextTopics"] == ["trade-off analysis"]


def test_topic_mastery_returns_weak_topics(monkeypatch):
    user_id = uuid.uuid4()
    fake_session = _FakeSession(
        mastery=[
            SimpleNamespace(
                user_id=user_id,
                topic="distributed systems",
                attempts_count=2,
                average_score=4.6,
                weakest_dimension="tradeOffReasoning",
                last_practiced_at=datetime(2026, 4, 23, 12, 0, tzinfo=timezone.utc),
            )
        ]
    )

    def override_get_db_session():
        yield fake_session

    monkeypatch.setattr(exercises_api, "UserTopicMastery", _FakeTopicMasteryModel)
    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[require_current_user] = _override_current_user(user_id)

    with TestClient(app) as client:
        response = client.get("/api/v1/topic-mastery")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["data"][0]["topic"] == "distributed systems"
    assert response.json()["data"][0]["lastPracticedAt"] == "2026-04-23T12:00:00Z"
