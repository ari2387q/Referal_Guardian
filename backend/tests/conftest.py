"""
Shared pytest fixtures for Referral Guardian tests.
"""
import os
import pytest

TEST_DB_PATH = "./test_referral.db"
os.environ["LLM_PROVIDER"] = "mock"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

from app.models.database import Base, engine, SessionLocal
from app.models.models import Case, Specialist, Appointment, CaseEvent


@pytest.fixture(scope="session", autouse=True)
def setup_shared_test_db():
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except OSError:
            pass

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Seed test specialist
    spec = Specialist(
        id="SPEC-101",
        name="Dr. Vance",
        specialization="Speech-Language Pathologist",
        availability_status="AVAILABLE",
        active=True,
    )
    db.add(spec)

    # Seed stuck specialist case
    c1 = Case(
        id="CASE-1042",
        child_identifier="STU-8821",
        referral_type="Speech-Language Evaluation",
        status="STUCK",
        current_bottleneck="SPECIALIST_UNAVAILABLE",
    )
    db.add(c1)

    # Seed repeated failure case
    c2 = Case(
        id="CASE-1043",
        child_identifier="STU-9922",
        referral_type="IEP Behavioral Assessment",
        status="STUCK",
        followup_attempts=3,
        current_bottleneck="REPEATED_FAILURE",
    )
    db.add(c2)

    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except OSError:
            pass


@pytest.fixture
def minimal_case() -> dict:
    return {
        "id": "CASE-TEST-001",
        "status": "STUCK",
        "specialist_status": "AVAILABLE",
        "required_documents_missing": False,
        "waiting_for_specialist": False,
        "appointment_delayed": False,
        "failed_attempts": 0,
        "followup_attempts": 0,
    }


@pytest.fixture
def empty_timeline() -> list:
    return []


@pytest.fixture
def sample_timeline() -> list:
    return [
        {"event_type": "REFERRAL_CREATED", "timestamp": "2024-01-01T10:00:00"},
        {"event_type": "SPECIALIST_CONTACTED", "timestamp": "2024-01-02T10:00:00"},
        {"event_type": "NO_RESPONSE", "timestamp": "2024-01-05T10:00:00"},
        {"event_type": "FOLLOWUP_SENT", "timestamp": "2024-01-08T10:00:00"},
        {"event_type": "NO_RESPONSE", "timestamp": "2024-01-11T10:00:00"},
        {"event_type": "FOLLOWUP_SENT", "timestamp": "2024-01-14T10:00:00"},
        {"event_type": "NO_RESPONSE", "timestamp": "2024-01-17T10:00:00"},
    ]
