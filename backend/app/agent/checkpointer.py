"""
LangGraph Checkpointer factory.

Uses PostgresSaver backed by the same Supabase/Postgres database when
DATABASE_URL points to a Postgres instance. Falls back to SqliteSaver
for local SQLite development.
"""
import logging
import os

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/referral_guardian",
)


def get_checkpointer():
    """
    Return an appropriate LangGraph checkpointer.

    - Postgres: uses langgraph-checkpoint-postgres (PostgresSaver)
    - SQLite / fallback: uses langgraph built-in MemorySaver (good enough for demo)

    The checkpointer enables graph state to survive backend restarts,
    which is required for the human-in-the-loop approval flow.
    """
    if DATABASE_URL.startswith("postgresql") or DATABASE_URL.startswith("postgres"):
        try:
            from psycopg_pool import ConnectionPool
            from langgraph.checkpoint.postgres import PostgresSaver

            # Convert SQLAlchemy-style URL to psycopg3 style if needed
            conn_string = DATABASE_URL.replace("postgresql+psycopg2://", "postgresql://")
            conn_string = conn_string.replace("postgresql+psycopg://", "postgresql://")

            pool = ConnectionPool(conn_string, max_size=5, open=True)
            checkpointer = PostgresSaver(pool)
            checkpointer.setup()  # create checkpoint tables if they don't exist
            logger.info("Using PostgresSaver checkpointer")
            return checkpointer

        except Exception as exc:
            logger.warning(
                "PostgresSaver unavailable (%s). Falling back to MemorySaver.", exc
            )

    # Fallback: in-memory (state lost on restart, fine for demo)
    from langgraph.checkpoint.memory import MemorySaver

    logger.info("Using MemorySaver checkpointer (in-memory, not persistent)")
    return MemorySaver()
