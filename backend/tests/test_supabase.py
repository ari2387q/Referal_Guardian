"""
Tests for Supabase Client integration.
Verifies connection to the user's Supabase project using the publishable key.
"""
import os
import pytest

from app.services.supabase_client import (
    SUPABASE_URL,
    SUPABASE_KEY,
    get_supabase,
    supabase_get_cases,
    supabase_get_case,
    supabase_get_timeline,
    supabase_insert,
)


def test_supabase_credentials_configured():
    assert "supabase.co" in SUPABASE_URL
    assert SUPABASE_KEY.startswith("sb_") or len(SUPABASE_KEY) > 10


def test_get_supabase_client():
    client = get_supabase()
    assert client is not None


def test_supabase_query_cases_safe():
    cases = supabase_get_cases()
    assert isinstance(cases, list)


def test_supabase_query_timeline_safe():
    timeline = supabase_get_timeline("CASE-1042")
    assert isinstance(timeline, list)


def test_supabase_insert_safe_with_rls():
    # If RLS blocks anon insert, function must return None safely without raising an unhandled exception
    res = supabase_insert("actions", {
        "case_id": "CASE-1042",
        "action_type": "CONTACT_SPECIALIST",
        "status": "SIMULATED",
    })
    # Either returns inserted dict or None (handled error)
    assert res is None or isinstance(res, dict)
