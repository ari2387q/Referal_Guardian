from typing import Any, Optional, TypedDict


class ReferralState(TypedDict, total=False):
    """
    State carried through the Referral Guardian LangGraph.

    PostgreSQL (Supabase) remains the source of truth for case data.
    This state captures the current agent execution context.
    """
    # --- Input ---
    case_id: str
    run_id: str          # AgentRun.id from the DB

    # --- Observed data ---
    case: dict[str, Any]
    timeline: list[dict[str, Any]]
    specialists: list[dict[str, Any]]
    current_state: Optional[str]

    # --- Agent analysis ---
    bottleneck: Optional[dict[str, Any]]
    recommendation: Optional[dict[str, Any]]
    recommendation_id: Optional[str]   # DB ID of the saved AgentRecommendation
    educator_summary: Optional[str]

    # --- Human decision ---
    human_decision: Optional[str]          # APPROVE | REJECT | MODIFY
    human_modification: Optional[dict[str, Any]]   # {action: "...", reason: "..."}

    # --- Execution ---
    action_result: Optional[dict[str, Any]]

    # --- Verification ---
    verification: Optional[dict[str, Any]]

    # --- Control flow ---
    requires_approval: bool
    should_continue: bool
    step_count: int

    # --- Error tracking ---
    error: Optional[str]
