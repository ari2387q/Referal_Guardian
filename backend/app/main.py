import uuid
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .models.database import Base, engine, get_db, SessionLocal
from .models.models import Case, CaseEvent, Specialist


def seed_data(db: Session):
    # Seed only if cases table is empty
    existing_cases = db.query(Case).first()
    if existing_cases:
        return

    # Seed Specialists
    spec_1 = Specialist(
        id=str(uuid.uuid4()),
        name="Dr. Meena Rao",
        specialization="Occupational Therapy",
        availability_status="AVAILABLE",
        active=True,
    )
    spec_2 = Specialist(
        id=str(uuid.uuid4()),
        name="Mr. James Okafor",
        specialization="Speech-Language Pathology",
        availability_status="UNAVAILABLE",
        active=True,
    )
    db.add_all([spec_1, spec_2])

    now = datetime.utcnow()

    # Seed Cases
    case_1001 = Case(
        id="CASE-1001",
        child_identifier="STU-004",
        referral_type="IEP Behavioral Assessment",
        status="ACTIVE",
        coordinator_id="COORD-01",
        current_bottleneck="SPECIALIST_UNAVAILABLE",
        created_date=now - timedelta(days=14),
        last_activity=now - timedelta(days=3),
        followup_attempts=3,
    )

    case_1002 = Case(
        id="CASE-1002",
        child_identifier="STU-007",
        referral_type="Speech Therapy Evaluation",
        status="NEW",
        coordinator_id=None,
        current_bottleneck=None,
        created_date=now - timedelta(days=2),
        last_activity=now - timedelta(days=2),
        followup_attempts=0,
    )
    db.add_all([case_1001, case_1002])

    # Events for CASE-1001
    event_1 = CaseEvent(
        id=str(uuid.uuid4()),
        case_id="CASE-1001",
        event_type="REFERRAL_CREATED",
        details="Referral submitted for STU-004",
        timestamp=now - timedelta(days=14),
    )
    event_2 = CaseEvent(
        id=str(uuid.uuid4()),
        case_id="CASE-1001",
        event_type="SPECIALIST_CONTACTED",
        details="Outreach sent to Dr. Meena Rao",
        timestamp=now - timedelta(days=10),
    )
    event_3 = CaseEvent(
        id=str(uuid.uuid4()),
        case_id="CASE-1001",
        event_type="NO_RESPONSE",
        details="No response after 7 days",
        timestamp=now - timedelta(days=3),
    )
    db.add_all([event_1, event_2, event_3])

    db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables
    Base.metadata.create_all(bind=engine)
    # Seed baseline mock data
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Referral Guardian API",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    cases = db.query(Case).all()
    now = datetime.utcnow()
    total_cases = len(cases)
    active_cases = sum(1 for c in cases if c.status == "ACTIVE")
    resolved_cases = sum(1 for c in cases if c.status == "RESOLVED")
    bottleneck_cases = sum(1 for c in cases if c.current_bottleneck)

    avg_days_open = 0.0
    if total_cases > 0:
        total_days = sum(max(0, (now - c.created_date).days) for c in cases)
        avg_days_open = round(total_days / total_cases, 1)

    return {
        "total_cases": total_cases,
        "active_cases": active_cases,
        "resolved_cases": resolved_cases,
        "bottleneck_cases": bottleneck_cases,
        "avg_days_open": avg_days_open,
    }


@app.get("/api/cases")
def list_cases(db: Session = Depends(get_db)):
    cases = db.query(Case).order_by(Case.created_date.desc()).all()
    now = datetime.utcnow()
    return [
        {
            "id": c.id,
            "child_identifier": c.child_identifier,
            "referral_type": c.referral_type,
            "status": c.status,
            "current_bottleneck": c.current_bottleneck,
            "days_open": max(0, (now - c.created_date).days),
            "followup_attempts": c.followup_attempts,
        }
        for c in cases
    ]


@app.get("/api/cases/{case_id}")
def get_case(case_id: str, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    events = (
        db.query(CaseEvent)
        .filter(CaseEvent.case_id == case_id)
        .order_by(CaseEvent.timestamp.asc())
        .all()
    )

    now = datetime.utcnow()
    return {
        "id": case.id,
        "child_identifier": case.child_identifier,
        "referral_type": case.referral_type,
        "status": case.status,
        "coordinator_id": case.coordinator_id,
        "current_bottleneck": case.current_bottleneck,
        "created_date": case.created_date.isoformat(),
        "last_activity": case.last_activity.isoformat(),
        "days_open": max(0, (now - case.created_date).days),
        "followup_attempts": case.followup_attempts,
        "events": [
            {
                "id": e.id,
                "case_id": e.case_id,
                "event_type": e.event_type,
                "details": e.details,
                "timestamp": e.timestamp.isoformat(),
            }
            for e in events
        ],
    }
