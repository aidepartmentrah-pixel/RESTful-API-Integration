import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.core.database import Base, get_db
from app.main import app
from app.models import Doctor, Patient, Worker

TEST_API_KEY = "test-api-key"

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def _configure_settings(monkeypatch):
    monkeypatch.setenv("API_KEY", TEST_API_KEY)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    db_session.add(
        Patient(
            patient_id="10025",
            first_name_ar="Ahmad",
            first_name_en="Ahmad",
            father_name_ar="Mohammed",
            father_name_en="Mohammed",
            last_name_ar="Ali",
            last_name_en="Ali",
            age=46,
            sex="Male",
        )
    )
    db_session.add(
        Doctor(
            doctor_id="1025",
            full_name="Dr. Ahmad Mohammed",
            first_name="Ahmad",
            father_name="Mohammed",
            specialty_name="Cardiology",
            is_active=True,
        )
    )
    db_session.add(
        Doctor(
            doctor_id="9999",
            full_name="Dr. Inactive One",
            specialty_name="Neurology",
            is_active=False,
        )
    )
    db_session.add(
        Worker(
            employee_id="5541",
            full_name="Hassan Ibrahim",
            job_title="Quality Assurance Specialist",
            is_active=True,
        )
    )
    db_session.add(
        Worker(
            employee_id="5542",
            full_name="Inactive Worker",
            is_active=False,
        )
    )
    db_session.commit()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers():
    return {"X-API-Key": TEST_API_KEY}
