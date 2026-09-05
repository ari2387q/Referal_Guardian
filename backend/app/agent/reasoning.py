"""
AI Reasoning — LLM-based recommendation layer.

The LLM receives structured case context and returns ONE recommended action.
It does not execute anything.

Supports LLM_PROVIDER=mock for local development without an OpenAI key.
"""
import json
import logging
import os
import re
from typing import Any

from app.agent.actions import ActionType, ALLOWED_ACTIONS

logger = logging.getLogger(__name__)

ALLOWED_ACTION_VALUES = {a.value for a in ALLOWED_ACTIONS}


# ---------------------------------------------------------------------------
# Mock provider (for dev / demo without an OpenAI key)
# ---------------------------------------------------------------------------

_MOCK_RECOMMENDATIONS: dict[str, dict[str, Any]] = {
    "SPECIALIST_UNAVAILABLE": {
        "action": "FIND_ALTERNATIVE_SPECIALIST",
        "reason": (
            "The assigned specialist is unavailable. Locating an alternative "
            "specialist is the most direct way to unblock the referral."
        ),
        "evidence": [
            "Assigned specialist marked as UNAVAILABLE",
            "No confirmed appointment exists",
        ],
        "confidence": 0.93,
    },
    "MISSING_DOCUMENT": {
        "action": "REQUEST_DOCUMENT",
        "reason": "Required documents are still pending. A document request will unblock processing.",
        "evidence": ["Document status is PENDING or MISSING"],
        "confidence": 0.97,
    },
    "NO_SPECIALIST_RESPONSE": {
        "action": "CONTACT_SPECIALIST",
        "reason": (
            "The specialist has not responded. A follow-up contact is the appropriate next step."
        ),
        "evidence": ["SPECIALIST_CONTACTED event exists", "No SPECIALIST_RESPONDED event"],
        "confidence": 0.88,
    },
    "APPOINTMENT_DELAYED": {
        "action": "SCHEDULE_FOLLOWUP",
        "reason": "The appointment is overdue. A follow-up should be scheduled.",
        "evidence": ["Appointment scheduled_date has passed", "Status still REQUESTED"],
        "confidence": 0.85,
    },
    "REPEATED_FAILURE": {
        "action": "ESCALATE_CASE",
        "reason": (
            "Multiple attempts to progress this referral have failed. "
            "Escalation is recommended to ensure the child receives timely services."
        ),
        "evidence": [
            "Three or more failed attempts detected in timeline",
            "No resolution after repeated follow-ups",
        ],
        "confidence": 0.95,
    },
}


def _mock_recommend(bottleneck: dict[str, Any]) -> dict[str, Any]:
    bottleneck_type = bottleneck.get("type", "")
    rec = _MOCK_RECOMMENDATIONS.get(
        bottleneck_type,
        {
            "action": "SCHEDULE_FOLLOWUP",
            "reason": "No specific bottleneck matched. Scheduling a follow-up to review.",
            "evidence": ["Generic follow-up recommended"],
            "confidence": 0.6,
        },
    )
    return rec.copy()


# ---------------------------------------------------------------------------
# LLM provider
# ---------------------------------------------------------------------------

def _get_llm():
    """Create the LLM. Import lazily to avoid import errors when PROVIDER=mock."""
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
    )


def _extract_json(content: str) -> dict[str, Any]:
    """Extract JSON from LLM response, handling markdown code fences."""
    # Strip markdown code fences
    content = re.sub(r"```(?:json)?\s*", "", content).strip().rstrip("`").strip()

    # Find JSON object boundaries
    start = content.find("{")
    end = content.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"No JSON object found in LLM response: {content[:200]}")
    return json.loads(content[start:end])


def _llm_recommend(
    case: dict[str, Any],
    timeline: list[dict[str, Any]],
    bottleneck: dict[str, Any],
    specialists: list[dict[str, Any]],
) -> dict[str, Any]:
    """Call the LLM and return a validated recommendation."""
    llm = _get_llm()
    allowed_actions = sorted(ALLOWED_ACTION_VALUES)

    specialists_section = (
        f"\nAVAILABLE SPECIALISTS (for FIND_ALTERNATIVE_SPECIALIST):\n"
        f"{json.dumps(specialists, indent=2, default=str)}\n"
        if specialists
        else ""
    )

    prompt = f"""You are Referral Guardian, an AI referral continuity assistant.

Your job is to analyze a referral case and recommend the next operational action
that a school staff member should consider taking.

IMPORTANT RULES:
- You MUST choose exactly ONE action from the ALLOWED ACTIONS list below.
- You MUST NOT execute any action yourself.
- Base your recommendation on the case data, timeline, and detected bottleneck.
- Prefer the smallest reasonable action that can unblock the referral.
- If 3 or more attempts have failed, consider ESCALATE_CASE.
- confidence must be between 0.0 and 1.0.

CASE:
{json.dumps(case, indent=2, default=str)}

TIMELINE (chronological):
{json.dumps(timeline, indent=2, default=str)}

DETECTED BOTTLENECK:
{json.dumps(bottleneck, indent=2, default=str)}
{specialists_section}
ALLOWED ACTIONS:
{json.dumps(allowed_actions, indent=2)}

Return ONLY valid JSON in exactly this format (no markdown, no extra text):

{{
    "action": "ONE_ALLOWED_ACTION",
    "reason": "Short explanation of why this action is appropriate.",
    "evidence": [
        "Relevant evidence from the case or timeline."
    ],
    "confidence": 0.0
}}
"""

    response = llm.invoke(prompt)
    content = response.content

    if isinstance(content, list):
        content = "".join(
            item.get("text", str(item)) if isinstance(item, dict) else str(item)
            for item in content
        )

    recommendation = _extract_json(content)
    return recommendation


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _validate_recommendation(recommendation: dict[str, Any]) -> dict[str, Any]:
    """Ensure the recommendation has a valid action and required fields."""
    action = recommendation.get("action")
    if action not in ALLOWED_ACTION_VALUES:
        raise ValueError(
            f"LLM returned invalid action '{action}'. "
            f"Allowed: {sorted(ALLOWED_ACTION_VALUES)}"
        )

    confidence = recommendation.get("confidence", 0.0)
    if not (0.0 <= float(confidence) <= 1.0):
        recommendation["confidence"] = max(0.0, min(1.0, float(confidence)))

    # Ensure evidence is a list
    if not isinstance(recommendation.get("evidence"), list):
        recommendation["evidence"] = [str(recommendation.get("evidence", ""))]

    return recommendation


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def recommend_action(
    case: dict[str, Any],
    timeline: list[dict[str, Any]],
    bottleneck: dict[str, Any],
    specialists: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Recommend the next operational action for a stuck referral case.

    Uses LLM_PROVIDER env var to choose between 'mock' and 'openai'.
    Returns a validated recommendation dict.
    """
    provider = os.getenv("LLM_PROVIDER", "mock").lower()
    specialists = specialists or []

    try:
        if provider == "mock":
            logger.info("Using mock LLM provider")
            recommendation = _mock_recommend(bottleneck)
        else:
            logger.info("Using OpenAI LLM provider")
            recommendation = _llm_recommend(case, timeline, bottleneck, specialists)

        return _validate_recommendation(recommendation)

    except ValueError:
        raise
    except Exception as exc:
        logger.exception("LLM recommendation failed, using mock fallback")
        # Fall back to mock on LLM error
        recommendation = _mock_recommend(bottleneck)
        recommendation["_fallback"] = True
        return _validate_recommendation(recommendation)
