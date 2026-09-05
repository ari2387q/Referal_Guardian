"""
Action Verification — deterministic result checking.

This is the in-memory verification layer (no DB).
For persisted verification, see action_executor.verify_and_persist().
"""
from typing import Any, Optional


def verify_action(
    action_result: Optional[dict[str, Any]],
) -> dict[str, Any]:
    """
    Verify the result of an executed action.

    Returns a structured verification dict with success, status, and reason.
    SUCCESS and SIMULATED are both considered verified outcomes.
    """
    if not action_result:
        return {
            "success": False,
            "status": "FAILED",
            "reason": "No action result was returned.",
        }

    status = action_result.get("status")

    if status in ("SUCCESS", "SIMULATED"):
        return {
            "success": True,
            "status": "VERIFIED",
            "reason": action_result.get("message", "Action completed successfully."),
        }

    return {
        "success": False,
        "status": "FAILED",
        "reason": action_result.get("error", "Action did not complete successfully."),
    }
