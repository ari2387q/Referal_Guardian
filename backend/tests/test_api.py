"""
End-to-end API tests for Referral Guardian.
Uses FastAPI TestClient with a file-based SQLite test database.
"""
import os
import pytest

TEST_DB_PATH = "./test_api_endpoints.db"
if os.path.exists(TEST_DB_PATH):
    try:
        os.remove(TEST_DB_PATH)
    except OSError:
        pass

os.environ["LLM_PROVIDER"] = "mock"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    return TestClient(app)


def test_dashboard_stats(client):
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "active_cases" in data
    assert "stuck_cases" in data
    assert "pending_actions" in data


def test_list_cases(client):
    res = client.get("/api/cases")
    assert res.status_code == 200
    cases = res.json()
    assert len(cases) >= 2
    case_ids = [c["id"] for c in cases]
    assert "CASE-1042" in case_ids
    assert "CASE-1043" in case_ids


def test_get_case_detail(client):
    res = client.get("/api/cases/CASE-1042")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == "CASE-1042"
    assert "timeline" in data


def test_get_nonexistent_case(client):
    res = client.get("/api/cases/CASE-99999")
    assert res.status_code == 404


def test_agent_run_pauses_for_approval(client):
    res = client.post("/api/cases/CASE-1042/agent/run")
    assert res.status_code == 200
    data = res.json()
    assert data["case_id"] == "CASE-1042"
    assert data["waiting_for_approval"] is True
    assert data["recommendation"] is not None
    assert data["recommendation"]["recommended_action"] in [
        "CONTACT_PARENT",
        "REQUEST_DOCUMENT",
        "CONTACT_SPECIALIST",
        "FIND_ALTERNATIVE_SPECIALIST",
        "SCHEDULE_FOLLOWUP",
        "ESCALATE_CASE",
    ]


def test_get_agent_state(client):
    res = client.get("/api/cases/CASE-1042/agent/state")
    assert res.status_code == 200
    data = res.json()
    assert data["case_id"] == "CASE-1042"
    assert data["waiting_for_approval"] is True


def test_agent_approve_and_verify(client):
    res = client.post(
        "/api/cases/CASE-1042/agent/approve",
        json={"approver_id": "coordinator-test"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["action_result"] is not None
    assert data["action_result"]["status"] in ("SUCCESS", "SIMULATED")


def test_modify_invalid_action(client):
    res = client.post(
        "/api/cases/CASE-1042/agent/modify",
        json={"action": "INVALID_ARBITRARY_ACTION"},
    )
    assert res.status_code == 400
