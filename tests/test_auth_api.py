import uuid
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.dependencies import get_db_session
from app.main import app


class _FakeUserQuery:
    def __init__(self, users):
        self._users = users

    def filter(self, predicate):
        return _FakeUserQuery([user for user in self._users if predicate.compare(user)])

    def one_or_none(self):
        if not self._users:
            return None
        return self._users[0]


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


class _FakeUserModel:
    email = _FakeColumn("email")
    id = _FakeColumn("id")

    def __init__(self, email, password_hash, full_name):
        self.id = uuid.uuid4()
        self.email = email
        self.password_hash = password_hash
        self.full_name = full_name


class _FakeSession:
    def __init__(self, users=None):
        self.users = list(users or [])
        self.committed = False

    def query(self, *_args, **_kwargs):
        return _FakeUserQuery(self.users)

    def add(self, obj):
        self.users.append(obj)

    def commit(self):
        self.committed = True

    def refresh(self, _obj):
        return None

    def close(self):
        return None


def test_register_returns_user_and_token(monkeypatch):
    fake_session = _FakeSession()

    def override_get_db_session():
        yield fake_session

    monkeypatch.setattr("app.api.auth.User", _FakeUserModel)
    monkeypatch.setattr("app.api.auth.hash_password", lambda password: f"hashed::{password}")
    monkeypatch.setattr("app.api.auth.create_access_token", lambda subject: f"token::{subject}")
    app.dependency_overrides[get_db_session] = override_get_db_session

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "andre@example.com",
                "password": "StrongPass1",
                "fullName": "Andre Butuc",
            },
        )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["data"]["user"]["email"] == "andre@example.com"
    assert response.json()["data"]["token"].startswith("token::")
    assert fake_session.committed is True


def test_login_returns_user_and_token(monkeypatch):
    user = SimpleNamespace(
        id=uuid.uuid4(),
        email="andre@example.com",
        password_hash="hashed",
        full_name="Andre Butuc",
    )
    fake_session = _FakeSession(users=[user])

    def override_get_db_session():
        yield fake_session

    monkeypatch.setattr("app.api.auth.User", _FakeUserModel)
    monkeypatch.setattr("app.api.auth.verify_password", lambda password, _: password == "StrongPass1")
    monkeypatch.setattr("app.api.auth.create_access_token", lambda subject: f"token::{subject}")
    app.dependency_overrides[get_db_session] = override_get_db_session

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "andre@example.com",
                "password": "StrongPass1",
            },
        )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["data"]["user"]["email"] == "andre@example.com"


def test_profile_requires_bearer_token():
    with TestClient(app) as client:
        response = client.get("/api/v1/profile")

    assert response.status_code == 401
