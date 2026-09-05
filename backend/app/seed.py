"""
Database Seeder for Referral Guardian Demo Scenarios.

Scenarios populated:
1. Stuck Specialist Demo (CASE-1042):
   - Child identified, referral created, assigned specialist is UNAVAILABLE
   - Agent detects SPECIALIST_UNAVAILABLE
   - Agent recommends FIND_ALTERNATIVE_SPECIALIST (Dr. Marcus Vance is available)
   - Staff approves -> Alternative specialist assigned -> verified

2. Repeated Failure / Escalation Demo (CASE-1043):
   - Multiple contacts with no response (3 attempts)
   - Agent detects REPEATED_FAILURE
   - Agent recommends ESCALATE_CASE
   - Staff approves -> Case escalated -> verified

3. Missing Document Demo (CASE-1044):
   - Case missing required medical history
   - Agent detects MISSING_DOCUMENT
   - Agent recommends REQUEST_DOCUMENT
"""
import datetime
from app.models.database import SessionLocal, engine, Base
from app.models.models import (
    Case,
    CaseEvent,
    Specialist,
    Appointment,
    Document,
    User,
)


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(Case).filter(Case.id == "CASE-1042").first():
            print("Database already contains demo cases.")
            return

        print("Seeding specialists...")
        spec1 = Specialist(
            id="SPEC-001",
            name="Dr. Sarah Jenkins",
            specialization="Speech-Language Pathologist",
            location="North District Clinic",
            availability_status="UNAVAILABLE",
            active=True,
        )
        spec2 = Specialist(
            id="SPEC-002",
            name="Dr. Marcus Vance",
            specialization="Speech-Language Pathologist",
            location="Metro Child Development Center",
            availability_status="AVAILABLE",
            next_available_date=datetime.datetime.utcnow() + datetime.timedelta(days=2),
            active=True,
        )
        spec3 = Specialist(
            id="SPEC-003",
            name="Dr. Elena Rostova",
            specialization="Occupational Therapist",
            location="Eastside Pediatrics",
            availability_status="AVAILABLE",
            next_available_date=datetime.datetime.utcnow() + datetime.timedelta(days=5),
            active=True,
        )
        spec4 = Specialist(
            id="SPEC-004",
            name="Dr. Robert Chen",
            specialization="Child Psychologist",
            location="Central Youth Wellness",
            availability_status="AVAILABLE",
            next_available_date=datetime.datetime.utcnow() + datetime.timedelta(days=3),
            active=True,
        )
        db.add_all([spec1, spec2, spec3, spec4])
        db.commit()

        print("Seeding demo cases...")
        now = datetime.datetime.utcnow()

        # CASE 1: Stuck Specialist
        c1 = Case(
            id="CASE-1042",
            child_identifier="STU-8821",
            referral_type="Speech-Language Evaluation",
            status="STUCK",
            current_bottleneck="SPECIALIST_UNAVAILABLE",
            created_date=now - datetime.timedelta(days=18),
            last_activity=now - datetime.timedelta(days=3),
            followup_attempts=2,
        )
        db.add(c1)
        db.flush()

        # Appointment with unavailable specialist
        appt1 = Appointment(
            id="APPT-1042",
            case_id="CASE-1042",
            specialist_id="SPEC-001",
            scheduled_date=now - datetime.timedelta(days=12),
            status="REQUESTED",
        )
        db.add(appt1)

        # Timeline for Case 1
        events1 = [
            CaseEvent(
                case_id="CASE-1042",
                event_type="REFERRAL_CREATED",
                details="Referral created by school coordinator Dr. Smith.",
                timestamp=now - datetime.timedelta(days=18),
            ),
            CaseEvent(
                case_id="CASE-1042",
                event_type="DOCUMENT_REQUESTED",
                details="Parent consent form requested.",
                timestamp=now - datetime.timedelta(days=16),
            ),
            CaseEvent(
                case_id="CASE-1042",
                event_type="DOCUMENT_RECEIVED",
                details="Parent consent form uploaded and verified.",
                timestamp=now - datetime.timedelta(days=14),
            ),
            CaseEvent(
                case_id="CASE-1042",
                event_type="SPECIALIST_CONTACTED",
                details="Outreach sent to assigned specialist Dr. Sarah Jenkins.",
                timestamp=now - datetime.timedelta(days=13),
            ),
            CaseEvent(
                case_id="CASE-1042",
                event_type="SPECIALIST_UNAVAILABLE",
                details="Dr. Sarah Jenkins responded: unavailable for new assessments until next term.",
                timestamp=now - datetime.timedelta(days=12),
            ),
            CaseEvent(
                case_id="CASE-1042",
                event_type="FOLLOWUP_SENT",
                details="Follow-up inquiry sent regarding potential openings.",
                timestamp=now - datetime.timedelta(days=6),
            ),
        ]
        db.add_all(events1)

        # CASE 2: Repeated Failure (Escalation demo)
        c2 = Case(
            id="CASE-1043",
            child_identifier="STU-9922",
            referral_type="IEP Behavioral Assessment",
            status="STUCK",
            current_bottleneck="REPEATED_FAILURE",
            created_date=now - datetime.timedelta(days=25),
            last_activity=now - datetime.timedelta(days=2),
            followup_attempts=3,
        )
        db.add(c2)
        db.flush()

        events2 = [
            CaseEvent(
                case_id="CASE-1043",
                event_type="REFERRAL_CREATED",
                details="Behavioral assessment referral created.",
                timestamp=now - datetime.timedelta(days=25),
            ),
            CaseEvent(
                case_id="CASE-1043",
                event_type="SPECIALIST_CONTACTED",
                details="Attempt 1: Initial outreach sent to clinic.",
                timestamp=now - datetime.timedelta(days=20),
            ),
            CaseEvent(
                case_id="CASE-1043",
                event_type="NO_RESPONSE",
                details="Attempt 1: No response received after 5 business days.",
                timestamp=now - datetime.timedelta(days=15),
            ),
            CaseEvent(
                case_id="CASE-1043",
                event_type="FOLLOWUP_SENT",
                details="Attempt 2: Second follow-up sent with high urgency.",
                timestamp=now - datetime.timedelta(days=12),
            ),
            CaseEvent(
                case_id="CASE-1043",
                event_type="NO_RESPONSE",
                details="Attempt 2: No response from provider.",
                timestamp=now - datetime.timedelta(days=7),
            ),
            CaseEvent(
                case_id="CASE-1043",
                event_type="FOLLOWUP_SENT",
                details="Attempt 3: Third follow-up dispatched.",
                timestamp=now - datetime.timedelta(days=4),
            ),
            CaseEvent(
                case_id="CASE-1043",
                event_type="NO_RESPONSE",
                details="Attempt 3: Unanswered. Multiple outreach attempts failed.",
                timestamp=now - datetime.timedelta(days=2),
            ),
        ]
        db.add_all(events2)

        # CASE 3: Missing Document
        c3 = Case(
            id="CASE-1044",
            child_identifier="STU-7711",
            referral_type="Physical Therapy Evaluation",
            status="STUCK",
            current_bottleneck="MISSING_DOCUMENT",
            created_date=now - datetime.timedelta(days=7),
            last_activity=now - datetime.timedelta(days=1),
            followup_attempts=1,
        )
        db.add(c3)
        db.flush()

        doc1 = Document(
            id="DOC-1044",
            case_id="CASE-1044",
            document_name="Pediatric_Physical_Therapy_Prescription.pdf",
            status="MISSING",
        )
        db.add(doc1)

        events3 = [
            CaseEvent(
                case_id="CASE-1044",
                event_type="REFERRAL_CREATED",
                details="Physical therapy evaluation initiated.",
                timestamp=now - datetime.timedelta(days=7),
            ),
            CaseEvent(
                case_id="CASE-1044",
                event_type="DOCUMENT_REQUESTED",
                details="Physician prescription required before therapy clinic can accept referral.",
                timestamp=now - datetime.timedelta(days=6),
            ),
        ]
        db.add_all(events3)

        db.commit()
        print("Database successfully seeded with demo cases and specialists!")

    except Exception as exc:
        db.rollback()
        print("Seeding error:", exc)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
