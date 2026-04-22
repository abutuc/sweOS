import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.core.security import hash_password
from app.core.tokens import create_access_token
from app.api.dependencies import get_db_session
from app.main import app
from app.models.user import User
from tests.db_utils import is_database_available, reset_public_schema


@pytest.fixture(scope="session")
def integration_engine():
    settings = get_settings()
    engine = create_engine(settings.database_url, future=True)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def migrated_db(integration_engine):
    if not is_database_available(integration_engine):
        pytest.skip("Postgres is not reachable at the configured database URL")
    reset_public_schema(integration_engine)
    yield integration_engine
    reset_public_schema(integration_engine)


@pytest.fixture
def db_session_factory(migrated_db):
    return sessionmaker(bind=migrated_db, autoflush=False, autocommit=False, expire_on_commit=False)


@pytest.fixture
def integration_client(db_session_factory):
    def override_get_db_session():
        db = db_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db_session] = override_get_db_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def authenticated_user(db_session_factory):
    db = db_session_factory()
    try:
        user = User(
            email="integration@example.com",
            password_hash=hash_password("StrongPass1"),
            full_name="Integration User",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        yield user
    finally:
        db.close()


@pytest.fixture
def auth_headers(authenticated_user):
    token = create_access_token(str(authenticated_user.id))
    return {"Authorization": f"Bearer {token}"}
