from app.scripts import seed_leetcode_exercises


class _FakeSession:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


def test_seed_leetcode_exercises_main_returns_created_count_and_closes_session(monkeypatch):
    fake_session = _FakeSession()

    def fake_session_local():
        return fake_session

    def fake_seed_leetcode_exercises(db):
        assert db is fake_session
        return 50

    monkeypatch.setattr(seed_leetcode_exercises, "SessionLocal", fake_session_local)
    monkeypatch.setattr(seed_leetcode_exercises, "seed_leetcode_exercises", fake_seed_leetcode_exercises)

    created_count = seed_leetcode_exercises.main()

    assert created_count == 50
    assert fake_session.closed is True
