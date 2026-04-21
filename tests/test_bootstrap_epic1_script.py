from types import SimpleNamespace

from app.scripts import bootstrap_epic1


class _FakeSession:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


def test_bootstrap_epic1_main_runs_full_bootstrap_flow(monkeypatch):
    called = {
        "create_all": None,
        "seeded_db": None,
        "bootstrapped_db": None,
    }
    fake_session = _FakeSession()
    fake_engine = object()

    class _FakeMetadata:
        def create_all(self, bind):
            called["create_all"] = bind

    class _FakeBase:
        metadata = _FakeMetadata()

    def fake_session_local():
        return fake_session

    def fake_get_or_create_default_user(db):
        called["bootstrapped_db"] = db
        return SimpleNamespace(email="default@sweos.local")

    def fake_seed_skill_catalog(db):
        called["seeded_db"] = db
        return 8

    monkeypatch.setattr(bootstrap_epic1, "Base", _FakeBase)
    monkeypatch.setattr(bootstrap_epic1, "engine", fake_engine)
    monkeypatch.setattr(bootstrap_epic1, "SessionLocal", fake_session_local)
    monkeypatch.setattr(
        bootstrap_epic1,
        "get_or_create_default_user",
        fake_get_or_create_default_user,
    )
    monkeypatch.setattr(
        bootstrap_epic1,
        "seed_skill_catalog",
        fake_seed_skill_catalog,
    )

    result = bootstrap_epic1.main()

    assert called["create_all"] is fake_engine
    assert called["bootstrapped_db"] is fake_session
    assert called["seeded_db"] is fake_session
    assert fake_session.closed is True
    assert result == {
        "user_email": "default@sweos.local",
        "created_skills": 8,
    }
