from types import SimpleNamespace

from app.scripts import seed_default_user


class _FakeSession:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


def test_seed_default_user_main_returns_user_and_closes_session(monkeypatch):
    fake_session = _FakeSession()
    expected_user = SimpleNamespace(email="default@sweos.local")

    def fake_session_local():
        return fake_session

    def fake_get_or_create_default_user(db):
        assert db is fake_session
        return expected_user

    monkeypatch.setattr(seed_default_user, "SessionLocal", fake_session_local)
    monkeypatch.setattr(
        seed_default_user,
        "get_or_create_default_user",
        fake_get_or_create_default_user,
    )

    user = seed_default_user.main()

    assert user is expected_user
    assert fake_session.closed is True
