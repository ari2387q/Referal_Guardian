"""
Supabase Client Service for Referral Guardian.

Connects to Supabase using the official supabase-py SDK.
Supports both the publishable/anon key and service_role key.
"""
import logging
import os
from typing import Any, Optional

from supabase import Client, create_client

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv(
    "SUPABASE_URL",
    "https://dlhhdjpyhlriinjpzzce.supabase.co",
)

SUPABASE_KEY = os.getenv(
    "SUPABASE_KEY",
    os.getenv(
        "SUPABASE_PUBLISHABLE_KEY",
        "sb_publishable_519NaqrpYJdiATVg7ZZewQ_MgNNJJoS",
    ),
)

_client: Optional[Client] = None


def get_supabase() -> Optional[Client]:
    """Return the Supabase client singleton."""
    global _client
    if _client is not None:
        return _client

    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning("SUPABASE_URL or SUPABASE_KEY is missing.")
        return None

    try:
        from supabase.client import ClientOptions
        options = ClientOptions(postgrest_client_timeout=3)
        _client = create_client(SUPABASE_URL, SUPABASE_KEY, options=options)
        logger.info("Supabase client initialized for %s", SUPABASE_URL)
        return _client
    except Exception as exc:
        logger.exception("Failed to initialize Supabase client: %s", exc)
        return None


# ---------------------------------------------------------------------------
# High-level Supabase operations with safe error handling
# ---------------------------------------------------------------------------

def supabase_get_cases() -> list[dict[str, Any]]:
    client = get_supabase()
    if not client:
        return []
    try:
        res = client.table("cases").select("*").execute()
        return res.data or []
    except Exception as exc:
        logger.warning("Supabase select cases error: %s", exc)
        return []


def supabase_get_case(case_id: str) -> Optional[dict[str, Any]]:
    client = get_supabase()
    if not client:
        return None
    try:
        res = client.table("cases").select("*").eq("id", case_id).limit(1).execute()
        if res.data:
            return res.data[0]
        return None
    except Exception as exc:
        logger.warning("Supabase select case %s error: %s", case_id, exc)
        return None


def supabase_get_timeline(case_id: str) -> list[dict[str, Any]]:
    client = get_supabase()
    if not client:
        return []
    # Try ordering by `timestamp` first (post-migration); fall back to `created_at`
    for order_col in ("timestamp", "created_at"):
        try:
            res = (
                client.table("case_events")
                .select("*")
                .eq("case_id", case_id)
                .order(order_col)
                .execute()
            )
            return res.data or []
        except Exception as exc:
            logger.warning(
                "Supabase select timeline for case %s (order=%s) error: %s",
                case_id, order_col, exc,
            )
    return []


def supabase_insert(table: str, data: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Safely insert a record into Supabase."""
    client = get_supabase()
    if not client:
        return None
    try:
        res = client.table(table).insert(data).execute()
        if res.data:
            return res.data[0]
        return None
    except Exception as exc:
        logger.warning("Supabase insert into %s failed (RLS/network): %s", table, exc)
        return None
