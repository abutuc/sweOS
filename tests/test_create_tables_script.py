from app.scripts import create_tables


def test_create_tables_main_calls_metadata_create_all(monkeypatch):
    called = {}

    class _FakeMetadata:
        def create_all(self, bind):
            called["bind"] = bind

    class _FakeBase:
        metadata = _FakeMetadata()

    fake_engine = object()

    monkeypatch.setattr(create_tables, "Base", _FakeBase)
    monkeypatch.setattr(create_tables, "engine", fake_engine)

    create_tables.main()

    assert called == {"bind": fake_engine}
