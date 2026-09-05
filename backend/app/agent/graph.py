"""
Referral Guardian LangGraph — graph definition.

Architecture:
  START → observe → detect_bottleneck → reason → approval (interrupt)
       → execute → verify
         ↗ (failure loop back to detect_bottleneck)

Human approval pauses at the `approval` node.
Failure after verify loops back to detect_bottleneck (new recommendation cycle).
"""
import logging

from langgraph.graph import END, START, StateGraph

from .checkpointer import get_checkpointer
from .nodes import (
    approval_node,
    bottleneck_node,
    execute_node,
    observe_node,
    reasoning_node,
    verification_node,
)
from .state import ReferralState

logger = logging.getLogger(__name__)

_MAX_STEPS = 10   # guard against infinite loops


# ---------------------------------------------------------------------------
# Conditional edge functions
# ---------------------------------------------------------------------------

def _after_bottleneck(state: ReferralState) -> str:
    """If a bottleneck was found, proceed to reasoning; otherwise end."""
    if state.get("bottleneck") and state.get("should_continue", True):
        return "reason"
    return END


def _after_approval(state: ReferralState) -> str:
    """Route based on human decision."""
    decision = state.get("human_decision", "REJECT")
    if decision in ("APPROVE", "MODIFY") and state.get("should_continue", True):
        return "execute"
    return END


def _after_verify(state: ReferralState) -> str:
    """
    On success → END (monitoring continues via Celery).
    On failure → loop back to detect_bottleneck for a new recommendation cycle.
    Guard: if step_count exceeds limit, END to avoid infinite loops.
    """
    step_count = state.get("step_count", 0) + 1
    if not state.get("verification", {}).get("success", False):
        if step_count < _MAX_STEPS:
            logger.info("Verification failed — looping back to bottleneck detection")
            return "detect_bottleneck"
    return END


def _increment_step(state: ReferralState) -> dict:
    return {"step_count": (state.get("step_count", 0) + 1)}


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def build_graph(checkpointer=None):
    graph = StateGraph(ReferralState)

    # Nodes
    graph.add_node("observe", observe_node)
    graph.add_node("detect_bottleneck", bottleneck_node)
    graph.add_node("reason", reasoning_node)
    graph.add_node("approval", approval_node)
    graph.add_node("execute", execute_node)
    graph.add_node("verify", verification_node)

    # Edges — main flow
    graph.add_edge(START, "observe")
    graph.add_edge("observe", "detect_bottleneck")

    # Conditional: bottleneck found?
    graph.add_conditional_edges(
        "detect_bottleneck",
        _after_bottleneck,
        {"reason": "reason", END: END},
    )

    graph.add_edge("reason", "approval")

    # Conditional: human approved?
    graph.add_conditional_edges(
        "approval",
        _after_approval,
        {"execute": "execute", END: END},
    )

    graph.add_edge("execute", "verify")

    # Conditional: verification success or failure loop
    graph.add_conditional_edges(
        "verify",
        _after_verify,
        {"detect_bottleneck": "detect_bottleneck", END: END},
    )

    if checkpointer is None:
        checkpointer = get_checkpointer()

    return graph.compile(
        checkpointer=checkpointer,
    )


# ---------------------------------------------------------------------------
# Singleton graph instance
# ---------------------------------------------------------------------------

_graph = None


def get_graph():
    """Return the compiled graph (lazily initialised)."""
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph
