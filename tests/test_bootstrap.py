from types import SimpleNamespace

from app.core import bootstrap


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

    def __init__(self, email, password_hash, full_name):
        self.email = email
        self.password_hash = password_hash
        self.full_name = full_name


class _FakeQuery:
    def __init__(self, items):
        self._items = items

    def filter(self, predicate):
        return _FakeQuery([item for item in self._items if predicate.compare(item)])

    def one_or_none(self):
        if not self._items:
            return None
        return self._items[0]


class _FakeSession:
    def __init__(self, users=None):
        self.users = list(users or [])
        self.added = []
        self.committed = False
        self.refreshed = []

    def query(self, *_args, **_kwargs):
        return _FakeQuery(self.users)

    def add(self, obj):
        self.added.append(obj)
        self.users.append(obj)

    def commit(self):
        self.committed = True

    def refresh(self, obj):
        self.refreshed.append(obj)


def test_get_or_create_default_user_returns_existing_user(monkeypatch):
    existing_user = SimpleNamespace(email=bootstrap.DEFAULT_USER_EMAIL)
    fake_session = _FakeSession(users=[existing_user])
    monkeypatch.setattr(bootstrap, "User", _FakeUserModel)

    user = bootstrap.get_or_create_default_user(fake_session)

    assert user is existing_user
    assert fake_session.added == []
    assert fake_session.committed is False
    assert fake_session.refreshed == []


def test_get_or_create_default_user_creates_missing_user(monkeypatch):
    fake_session = _FakeSession()
    monkeypatch.setattr(bootstrap, "User", _FakeUserModel)

    user = bootstrap.get_or_create_default_user(fake_session)

    assert user.email == bootstrap.DEFAULT_USER_EMAIL
    assert user.password_hash == "disabled"
    assert user.full_name == "Default User"
    assert fake_session.added == [user]
    assert fake_session.committed is True
    assert fake_session.refreshed == [user]
