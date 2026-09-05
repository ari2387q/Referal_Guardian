"""
Case Service — data access layer for the agent.

All database reads needed by the agent go through here,
keeping nodes thin and testable.
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.models import (
    AgentRun,
    AgentRunStep,
    Appointment,
    Case,
    CaseEvent,
    Specialist,
)

from app.services.supabase_client import (
    supabase_get_case,
    supabase_get_timeline,
    supabase_insert,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Case retrieval
# ---------------------------------------------------------------------------

def get_case(db: Session, case_id: str) -> Optional[dict[str, Any]]:
    """Return a flat dict representation of the case, checking Supabase and local DB."""
    # Check Supabase first if available
    sb_case = supabase_get_case(case_id)
    if sb_case:
        # Standardize keys from Supabase
        return {
            "id": sb_case.get("id", case_id),
            "child_identifier": sb_case.get("child_identifier") or sb_case.get("child_id", "STU-UNKNOWN"),
            "referral_type": sb_case.get("referral_type", "Evaluation"),
            "status": sb_case.get("status", "STUCK"),
            "coordinator_id": sb_case.get("coordinator_id"),
            "assigned_specialist_id": sb_case.get("assigned_specialist_id"),
            "current_bottleneck": sb_case.get("current_bottleneck") or sb_case.get("bottleneck"),
            "coordinator_notes": sb_case.get("coordinator_notes"),
            "diagnostic_details": sb_case.get("diagnostic_details"),
            "created_date": sb_case.get("created_date"),
            "days_open": sb_case.get("days_open", 0),
            "followup_attempts": sb_case.get("followup_attempts", 0),
            "specialist_status": sb_case.get("specialist_status", "NONE"),
            "required_documents_missing": bool(sb_case.get("required_documents_missing")),
            "waiting_for_specialist": bool(sb_case.get("waiting_for_specialist")),
            "appointment_delayed": bool(sb_case.get("appointment_delayed")),
            "failed_attempts": sb_case.get("failed_attempts", sb_case.get("followup_attempts", 0)),
        }

    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        return None
    return _case_to_dict(case)


def _case_to_dict(case: Case) -> dict[str, Any]:
    specialist_name = None
    if case.assigned_specialist:
        specialist_name = case.assigned_specialist.name
    elif case.appointments:
        latest = sorted(case.appointments, key=lambda a: a.scheduled_date or datetime.min)[-1]
        if latest.specialist:
            specialist_name = latest.specialist.name

    return {
        "id": case.id,
        "child_identifier": case.child_identifier,
        "referral_type": case.referral_type,
        "status": case.status,
        "coordinator_id": case.coordinator_id,
        "assigned_specialist_id": case.assigned_specialist_id,
        "assigned_specialist_name": specialist_name,
        "current_bottleneck": case.current_bottleneck,
        "current_responsible_person": case.current_responsible_person,
        "coordinator_notes": case.coordinator_notes,
        "diagnostic_details": case.diagnostic_details,
        "created_date": case.created_date.isoformat() if case.created_date else None,
        "last_activity": case.last_activity.isoformat() if case.last_activity else None,
        "next_followup_date": (
            case.next_followup_date.isoformat() if case.next_followup_date else None
        ),
        "followup_attempts": case.followup_attempts or 0,
        "days_open": (
            (datetime.utcnow() - case.created_date).days if case.created_date else 0
        ),
        # Derived fields the bottleneck detector uses
        "specialist_status": _get_specialist_status(case),
        "required_documents_missing": _has_missing_documents(case),
        "waiting_for_specialist": _is_waiting_for_specialist(case),
        "appointment_delayed": _is_appointment_delayed(case),
        "failed_attempts": case.followup_attempts or 0,
    }


def _get_specialist_status(case: Case) -> str:
    """Derive specialist status from the most recent appointment."""
    if not case.appointments:
        return "NONE"
    latest = sorted(case.appointments, key=lambda a: a.scheduled_date or datetime.min)[-1]
    if latest.specialist and not latest.specialist.active:
        return "UNAVAILABLE"
    if latest.specialist and latest.specialist.availability_status == "UNAVAILABLE":
        return "UNAVAILABLE"
    return "AVAILABLE"


def _has_missing_documents(case: Case) -> bool:
    return any(d.status in ("PENDING", "MISSING") for d in case.documents)


def _is_waiting_for_specialist(case: Case) -> bool:
    """True if there has been a CONTACT_SPECIALIST event without a follow-up response."""
    event_types = [e.event_type for e in case.events]
    return (
        "SPECIALIST_CONTACTED" in event_types
        and "SPECIALIST_RESPONDED" not in event_types
        and "APPOINTMENT_CONFIRMED" not in event_types
    )


def _is_appointment_delayed(case: Case) -> bool:
    """True if an appointment was scheduled in the past but still REQUESTED."""
    now = datetime.utcnow()
    return any(
        a.scheduled_date and a.scheduled_date < now and a.status == "REQUESTED"
        for a in case.appointments
    )


# ---------------------------------------------------------------------------
# Timeline retrieval
# ---------------------------------------------------------------------------

def get_case_timeline(db: Session, case_id: str) -> list[dict[str, Any]]:
    """Return all case events ordered chronologically, checking Supabase and local DB."""
    events = (
        db.query(CaseEvent)
        .filter(CaseEvent.case_id == case_id)
        .order_by(CaseEvent.timestamp)
        .all()
    )
    local_events = [
        {
            "id": e.id,
            "event_type": e.event_type,
            "details": e.details,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
        }
        for e in events
    ]

    sb_events = supabase_get_timeline(case_id)
    if sb_events:
        existing_ids = {e["id"] for e in local_events}
        for sbe in sb_events:
            if sbe.get("id") not in existing_ids:
                local_events.append({
                    "id": sbe.get("id"),
                    "event_type": sbe.get("event_type", "EVENT"),
                    "details": sbe.get("details"),
                    "timestamp": sbe.get("timestamp") or sbe.get("created_at"),
                })

    return local_events


def record_event(
    db: Session,
    case_id: str,
    event_type: str,
    details: Optional[str] = None,
) -> CaseEvent:
    """Insert a timeline event and update case.last_activity, syncing to Supabase."""
    event = CaseEvent(
        case_id=case_id,
        event_type=event_type,
        details=details,
    )
    db.add(event)

    case = db.query(Case).filter(Case.id == case_id).first()
    if case:
        case.last_activity = datetime.utcnow()

    db.commit()
    db.refresh(event)

    # Sync to Supabase case_events table
    supabase_insert("case_events", {
        "id": event.id,
        "case_id": case_id,
        "event_type": event_type,
        "details": details,
    })

    logger.info("Timeline event recorded: case=%s event=%s", case_id, event_type)
    return event


# ---------------------------------------------------------------------------
# Specialist queries
# ---------------------------------------------------------------------------

def get_available_specialists(
    db: Session, specialization: str
) -> list[dict[str, Any]]:
    """Return active, available specialists matching the given specialization."""
    specialists = (
        db.query(Specialist)
        .filter(
            Specialist.active.is_(True),
            Specialist.availability_status == "AVAILABLE",
            Specialist.specialization.ilike(f"%{specialization}%"),
        )
        .all()
    )
    return [
        {
            "id": s.id,
            "name": s.name,
            "specialization": s.specialization,
            "location": s.location,
            "next_available_date": (
                s.next_available_date.isoformat() if s.next_available_date else None
            ),
        }
        for s in specialists
    ]


def get_all_specialists(db: Session) -> list[dict[str, Any]]:
    """Return all active specialists (for the reasoning layer)."""
    specialists = (
        db.query(Specialist)
        .filter(Specialist.active.is_(True))
        .all()
    )
    return [
        {
            "id": s.id,
            "name": s.name,
            "specialization": s.specialization,
            "location": s.location,
            "availability_status": s.availability_status,
            "next_available_date": (
                s.next_available_date.isoformat() if s.next_available_date else None
            ),
        }
        for s in specialists
    ]


# ---------------------------------------------------------------------------
# Agent run tracking
# ---------------------------------------------------------------------------

def get_or_create_agent_run(db: Session, case_id: str) -> AgentRun:
    """Return the active agent run for a case, or create one."""
    thread_id = f"case-{case_id}"
    run = (
        db.query(AgentRun)
        .filter(
            AgentRun.case_id == case_id,
            AgentRun.status.in_(["RUNNING", "WAITING_APPROVAL"]),
        )
        .first()
    )
    if run:
        return run

    run = AgentRun(
        case_id=case_id,
        thread_id=thread_id,
        status="RUNNING",
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def complete_agent_run(db: Session, run_id: str, status: str = "COMPLETED") -> None:
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if run:
        run.status = status
        run.completed_at = datetime.utcnow()
        db.commit()


def record_run_step(
    db: Session,
    run_id: str,
    case_id: str,
    node_name: str,
    status: str = "COMPLETED",
    details: Optional[dict] = None,
) -> AgentRunStep:
    step = AgentRunStep(
        run_id=run_id,
        case_id=case_id,
        node_name=node_name,
        status=status,
        details=json.dumps(details) if details else None,
    )
    db.add(step)
    db.commit()
    return step


# ---------------------------------------------------------------------------
# Stuck cases for Celery monitoring
# ---------------------------------------------------------------------------

def get_stuck_cases(db: Session) -> list[dict[str, Any]]:
    """Return cases that are STUCK or ACTIVE but have had no activity in 24 h."""
    threshold = datetime.utcnow() - timedelta(hours=24)
    cases = (
        db.query(Case)
        .filter(
            Case.status.in_(["STUCK", "ACTIVE"]),
            Case.last_activity < threshold,
        )
        .all()
    )
    return [_case_to_dict(c) for c in cases]


def has_pending_recommendation(db: Session, case_id: str) -> bool:
    """True if there is already an unanswered recommendation for this case."""
    from app.models.models import AgentRecommendation
    return (
        db.query(AgentRecommendation)
        .filter(
            AgentRecommendation.case_id == case_id,
            AgentRecommendation.status == "PENDING",
        )
        .first()
        is not None
    )


# ---------------------------------------------------------------------------
# Case CRUD operations
# ---------------------------------------------------------------------------

def create_case(
    db: Session,
    child_identifier: str,
    referral_type: str,
    status: str = "NEW",
    coordinator_id: Optional[str] = None,
    assigned_specialist_id: Optional[str] = None,
    current_bottleneck: Optional[str] = None,
    coordinator_notes: Optional[str] = None,
    initial_event_details: Optional[str] = None,
) -> Case:
    """Create a new referral case and initial timeline event."""
    new_case = Case(
        child_identifier=child_identifier,
        referral_type=referral_type,
        status=status,
        coordinator_id=coordinator_id,
        assigned_specialist_id=assigned_specialist_id,
        current_bottleneck=current_bottleneck,
        coordinator_notes=coordinator_notes,
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)

    # Initial event
    evt_text = initial_event_details or f"Referral created for {child_identifier} ({referral_type})."
    record_event(db, new_case.id, "REFERRAL_CREATED", evt_text)

    # If specialist is assigned, create initial appointment link and event
    if assigned_specialist_id:
        appt = Appointment(
            case_id=new_case.id,
            specialist_id=assigned_specialist_id,
            scheduled_date=datetime.utcnow() + timedelta(days=5),
            status="REQUESTED",
        )
        db.add(appt)
        db.commit()
        record_event(db, new_case.id, "SPECIALIST_CONTACTED", "Initial outreach sent to assigned specialist.")

    # Sync to Supabase
    supabase_insert("cases", {
        "id": new_case.id,
        "child_identifier": child_identifier,
        "referral_type": referral_type,
        "status": status,
        "coordinator_id": coordinator_id,
        "assigned_specialist_id": assigned_specialist_id,
        "current_bottleneck": current_bottleneck,
        "coordinator_notes": coordinator_notes,
    })

    return new_case


def update_case(
    db: Session,
    case_id: str,
    updates: dict[str, Any],
) -> Optional[dict[str, Any]]:
    """Update case fields and record modification event if status or bottleneck changed."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        return None

    old_status = case.status
    old_bottleneck = case.current_bottleneck

    for k, v in updates.items():
        if hasattr(case, k):
            setattr(case, k, v)

    case.last_activity = datetime.utcnow()
    db.commit()
    db.refresh(case)

    if "status" in updates and updates["status"] != old_status:
        record_event(
            db, case_id, "STATUS_UPDATED",
            f"Case status changed from {old_status} to {updates['status']}."
        )

    if "current_bottleneck" in updates and updates["current_bottleneck"] != old_bottleneck:
        record_event(
            db, case_id, "BOTTLENECK_UPDATED",
            f"Bottleneck updated to: {updates['current_bottleneck']}."
        )

    return _case_to_dict(case)


def delete_case(db: Session, case_id: str) -> bool:
    """Delete a case and associated records."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        return False
    db.delete(case)
    db.commit()
    return True


def update_specialist_availability(
    db: Session,
    specialist_id: str,
    availability_status: str,
    next_available_date: Optional[datetime] = None,
) -> Optional[dict[str, Any]]:
    """Update specialist availability status."""
    spec = db.query(Specialist).filter(Specialist.id == specialist_id).first()
    if not spec:
        return None

    spec.availability_status = availability_status
    if next_available_date:
        spec.next_available_date = next_available_date
    db.commit()
    db.refresh(spec)

    return {
        "id": spec.id,
        "name": spec.name,
        "specialization": spec.specialization,
        "location": spec.location,
        "availability_status": spec.availability_status,
        "next_available_date": spec.next_available_date.isoformat() if spec.next_available_date else None,
        "active": spec.active,
    }


def update_diagnostic_details(
    db: Session,
    case_id: str,
    diagnostic_details: str,
    educator_name: Optional[str] = None,
) -> Optional[dict[str, Any]]:
    """Save diagnostic evaluation notes and add a timeline event."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        return None

    case.diagnostic_details = diagnostic_details
    case.last_activity = datetime.utcnow()
    db.commit()
    db.refresh(case)

    name_str = f" by {educator_name}" if educator_name else ""
    record_event(
        db,
        case_id,
        "DIAGNOSTIC_EVALUATION_LOGGED",
        f"Diagnostic assessment notes submitted{name_str}: {diagnostic_details[:100]}..."
    )

    return _case_to_dict(case)
