from app.scripts import seed_skill_catalog


class _FakeSession:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


def test_seed_skill_catalog_main_returns_created_count_and_closes_session(monkeypatch):
    fake_session = _FakeSession()

    def fake_session_local():
        return fake_session

    def fake_seed_skill_catalog(db):
        assert db is fake_session
        return 8

    monkeypatch.setattr(seed_skill_catalog, "SessionLocal", fake_session_local)
    monkeypatch.setattr(seed_skill_catalog, "seed_skill_catalog", fake_seed_skill_catalog)

    created_count = seed_skill_catalog.main()

    assert created_count == 8
    assert fake_session.closed is True
