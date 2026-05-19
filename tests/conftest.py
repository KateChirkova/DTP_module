# фикстуры pytest: in-memory SQLite, client, auth, internal API key
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.traffic_dtp.api.main import app
from src.traffic_dtp.db.models.user import User
from src.traffic_dtp.db.session import Base, get_db
from src.traffic_dtp.services.auth import hash_password

TEST_DATABASE_URL = "sqlite://"
TEST_INTERNAL_API_KEY = "test-internal-key"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def _internal_api_key_env(monkeypatch):
    monkeypatch.setenv("DTP_INTERNAL_API_KEY", TEST_INTERNAL_API_KEY)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def internal_headers():
    return {"X-Internal-Key": TEST_INTERNAL_API_KEY}


@pytest.fixture
def sample_user(db_session):
    # пользователь в той же in-memory SQLite, что и client
    login = "quality_test_user"
    password = "quality_pw_99"
    db_session.merge(
        User(
            login=login,
            password_hash=hash_password(password),
        )
    )
    db_session.commit()
    return {"login": login, "password": password}


@pytest.fixture
def auth_headers(client, sample_user):
    r = client.post(
        "/api/v1/auth/login",
        json={"login": sample_user["login"], "password": sample_user["password"]},
    )
    assert r.status_code == 200, r.text
    token = r.json()["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_token(auth_headers):
    return auth_headers["Authorization"].split(" ", 1)[1]
