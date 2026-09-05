"""
Action Executor — controlled side-effect layer.

All agent actions must pass through here.
The LLM recommends; this module executes — and only the allowed actions.
"""
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.agent.actions import ActionType
from app.models.models import (
    Action,
    ActionVerification,
    Appointment,
    Communication,
    Document,
    Escalation,
    FollowUp,
    Specialist,
    Case,
)
from app.services.case_service import record_event
from app.services.supabase_client import supabase_insert

logger = logging.getLogger(__name__)


def execute_action(
    case_id: str,
    action: str,
    db: Session,
    recommendation_id: Optional[str] = None,
    parameters: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Execute a controlled action and persist the result.

    Returns a structured result dict with status, action, message, entity_id.
    status is one of: SUCCESS, FAILED, SIMULATED
    """
    parameters = parameters or {}

    try:
        action_type = ActionType(action)
    except ValueError:
        logger.warning("Unsupported action requested: %s", action)
        return {
            "status": "FAILED",
            "action": action,
            "error": f"Unsupported action: {action}",
        }

    logger.info("Executing action: case=%s action=%s", case_id, action)

    try:
        if action_type == ActionType.CONTACT_PARENT:
            result = _contact_parent(db, case_id, parameters)

        elif action_type == ActionType.REQUEST_DOCUMENT:
            result = _request_document(db, case_id, parameters)

        elif action_type == ActionType.CONTACT_SPECIALIST:
            result = _contact_specialist(db, case_id, parameters)

        elif action_type == ActionType.FIND_ALTERNATIVE_SPECIALIST:
            result = _find_alternative_specialist(db, case_id, parameters)

        elif action_type == ActionType.SCHEDULE_FOLLOWUP:
            result = _schedule_followup(db, case_id, parameters)

        elif action_type == ActionType.ESCALATE_CASE:
            result = _escalate_case(db, case_id, parameters)

        else:
            result = {"status": "FAILED", "error": "Action not implemented."}

    except Exception as exc:
        logger.exception("Action execution failed: case=%s action=%s", case_id, action)
        result = {
            "status": "FAILED",
            "action": action,
            "error": str(exc),
        }

    # Persist the action record
    action_record = Action(
        case_id=case_id,
        recommendation_id=recommendation_id,
        action_type=action,
        status=result.get("status", "FAILED"),
        result_message=result.get("message") or result.get("error"),
        entity_id=result.get("entity_id"),
    )
    db.add(action_record)
    db.commit()
    db.refresh(action_record)

    # Sync to Supabase actions table
    supabase_insert("actions", {
        "id": action_record.id,
        "case_id": case_id,
        "action_type": action,
        "status": action_record.status,
        "result_message": action_record.result_message,
        "entity_id": action_record.entity_id,
    })

    result["action_record_id"] = action_record.id
    return result


# ---------------------------------------------------------------------------
# Individual action handlers
# ---------------------------------------------------------------------------

def _contact_parent(
    db: Session, case_id: str, parameters: dict[str, Any]
) -> dict[str, Any]:
    comm = Communication(
        case_id=case_id,
        recipient_type="PARENT",
        message=parameters.get("message", "Please contact us regarding the referral."),
        status="SENT",
    )
    db.add(comm)
    db.flush()

    record_event(
        db,
        case_id,
        "PARENT_CONTACTED",
        f"Communication sent to parent. ID: {comm.id}",
    )

    return {
        "status": "SIMULATED",
        "action": "CONTACT_PARENT",
        "message": "Parent contact communication created (simulated send).",
        "entity_id": comm.id,
    }


def _request_document(
    db: Session, case_id: str, parameters: dict[str, Any]
) -> dict[str, Any]:
    doc_name = parameters.get("document_name", "Required Document")
    doc = Document(
        case_id=case_id,
        document_name=doc_name,
        status="PENDING",
    )
    db.add(doc)
    db.flush()

    record_event(
        db,
        case_id,
        "DOCUMENT_REQUESTED",
        f"Document request created: {doc_name}. ID: {doc.id}",
    )

    return {
        "status": "SUCCESS",
        "action": "REQUEST_DOCUMENT",
        "message": f"Document request created: {doc_name}",
        "entity_id": doc.id,
    }


def _contact_specialist(
    db: Session, case_id: str, parameters: dict[str, Any]
) -> dict[str, Any]:
    specialist_id = parameters.get("specialist_id")
    comm = Communication(
        case_id=case_id,
        recipient_type="SPECIALIST",
        recipient_id=specialist_id,
        message=parameters.get(
            "message", "Please respond to the referral assignment."
        ),
        status="SENT",
    )
    db.add(comm)
    db.flush()

    record_event(
        db,
        case_id,
        "SPECIALIST_CONTACTED",
        f"Specialist contact communication created (simulated). Comm ID: {comm.id}",
    )

    return {
        "status": "SIMULATED",
        "action": "CONTACT_SPECIALIST",
        "message": "Specialist contact communication created (simulated send).",
        "entity_id": comm.id,
    }


def _find_alternative_specialist(
    db: Session, case_id: str, parameters: dict[str, Any]
) -> dict[str, Any]:
    specialist_id = parameters.get("specialist_id")
    if not specialist_id:
        # Try to find any available specialist
        specialist = (
            db.query(Specialist)
            .filter(
                Specialist.active.is_(True),
                Specialist.availability_status == "AVAILABLE",
            )
            .first()
        )
        if specialist:
            specialist_id = specialist.id
        else:
            return {
                "status": "FAILED",
                "action": "FIND_ALTERNATIVE_SPECIALIST",
                "error": "No available alternative specialists found in database.",
            }

    # Create a new appointment request with the alternative specialist
    appt = Appointment(
        case_id=case_id,
        specialist_id=specialist_id,
        status="REQUESTED",
        scheduled_date=datetime.utcnow() + timedelta(days=7),
    )
    db.add(appt)
    db.flush()

    record_event(
        db,
        case_id,
        "ALTERNATIVE_SPECIALIST_ASSIGNED",
        f"Alternative specialist {specialist_id} assigned. Appointment ID: {appt.id}",
    )

    return {
        "status": "SUCCESS",
        "action": "FIND_ALTERNATIVE_SPECIALIST",
        "message": f"Alternative specialist assigned. Appointment request created.",
        "entity_id": appt.id,
    }


def _schedule_followup(
    db: Session, case_id: str, parameters: dict[str, Any]
) -> dict[str, Any]:
    days_out = parameters.get("days_out", 3)
    followup_date = datetime.utcnow() + timedelta(days=days_out)

    followup = FollowUp(
        case_id=case_id,
        scheduled_for=followup_date,
        notes=parameters.get("notes", "Automated follow-up scheduled by Referral Guardian."),
    )
    db.add(followup)
    db.flush()

    # Update case next_followup_date
    case = db.query(Case).filter(Case.id == case_id).first()
    if case:
        case.next_followup_date = followup_date
        case.followup_attempts = (case.followup_attempts or 0) + 1

    record_event(
        db,
        case_id,
        "FOLLOWUP_SCHEDULED",
        f"Follow-up scheduled for {followup_date.isoformat()}. ID: {followup.id}",
    )

    return {
        "status": "SUCCESS",
        "action": "SCHEDULE_FOLLOWUP",
        "message": f"Follow-up scheduled for {followup_date.date()}.",
        "entity_id": followup.id,
    }


def _escalate_case(
    db: Session, case_id: str, parameters: dict[str, Any]
) -> dict[str, Any]:
    reason = parameters.get(
        "reason",
        "Multiple failed attempts to progress the referral. Escalated by Referral Guardian.",
    )
    escalation = Escalation(
        case_id=case_id,
        reason=reason,
        priority=parameters.get("priority", "HIGH"),
    )
    db.add(escalation)
    db.flush()

    # Update case status
    case = db.query(Case).filter(Case.id == case_id).first()
    if case:
        case.status = "ESCALATED"
        case.current_bottleneck = "ESCALATED"

    record_event(
        db,
        case_id,
        "CASE_ESCALATED",
        f"Case escalated. Reason: {reason}. Escalation ID: {escalation.id}",
    )

    return {
        "status": "SUCCESS",
        "action": "ESCALATE_CASE",
        "message": "Case has been escalated.",
        "entity_id": escalation.id,
    }


# ---------------------------------------------------------------------------
# Post-action verification helpers (called by verification node)
# ---------------------------------------------------------------------------

def verify_and_persist(
    db: Session,
    case_id: str,
    action_record_id: str,
    action_result: dict[str, Any],
) -> dict[str, Any]:
    """Verify the action result and persist an ActionVerification record."""
    status = action_result.get("status")
    success = status in ("SUCCESS", "SIMULATED")

    verification = ActionVerification(
        action_id=action_record_id,
        case_id=case_id,
        success=success,
        verification_status="VERIFIED" if success else "FAILED",
        reason=action_result.get("message") or action_result.get("error"),
    )
    db.add(verification)
    db.commit()

    # Sync to Supabase action_verifications table
    supabase_insert("action_verifications", {
        "id": verification.id,
        "action_id": action_record_id,
        "case_id": case_id,
        "success": success,
        "verification_status": verification.verification_status,
        "reason": verification.reason,
    })

    return {
        "success": success,
        "status": "VERIFIED" if success else "FAILED",
        "reason": verification.reason,
    }
