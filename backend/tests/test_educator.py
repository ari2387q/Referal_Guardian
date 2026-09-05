"""
Tests for Coordinator CRUD, Timeline Event Simulation, and Special Educator Portal.
"""
import pytest
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    return TestClient(app)


def test_coordinator_create_case_crud(client):
    # 1. Create case
    create_payload = {
        "child_identifier": "STU-TEST-900",
        "referral_type": "Speech Evaluation",
        "status": "STUCK",
        "current_bottleneck": "SPECIALIST_UNAVAILABLE",
        "coordinator_notes": "Initial referral notes from coordinator.",
    }
    res = client.post("/api/cases", json=create_payload)
    assert res.status_code == 200
    created = res.json()
    case_id = created["id"]
    assert created["child_identifier"] == "STU-TEST-900"
    assert created["coordinator_notes"] == "Initial referral notes from coordinator."
    assert "timeline" in created
    assert len(created["timeline"]) >= 1

    # 2. Add manual timeline event to test bottleneck triggers
    evt_res = client.post(f"/api/cases/{case_id}/events", json={
        "event_type": "NO_RESPONSE",
        "details": "Specialist failed to reply after second attempt.",
    })
    assert evt_res.status_code == 200
    evt_data = evt_res.json()
    assert evt_data["event_type"] == "NO_RESPONSE"

    # 3. Update case status
    update_res = client.put(f"/api/cases/{case_id}", json={
        "status": "ESCALATED",
        "coordinator_notes": "Updated note: escalating to clinical director.",
    })
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["status"] == "ESCALATED"
    assert updated["coordinator_notes"] == "Updated note: escalating to clinical director."

    # 4. Delete case
    del_res = client.delete(f"/api/cases/{case_id}")
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # 5. Verify deleted
    get_res = client.get(f"/api/cases/{case_id}")
    assert get_res.status_code == 404


def test_specialist_availability_and_diagnostics(client):
    # 1. List specialists
    specs_res = client.get("/api/specialists")
    assert specs_res.status_code == 200
    specs = specs_res.json()
    assert len(specs) >= 1
    spec_id = specs[0]["id"]

    # 2. Toggle specialist availability
    avail_res = client.patch(f"/api/educator/specialists/{spec_id}/availability", json={
        "availability_status": "UNAVAILABLE",
    })
    assert avail_res.status_code == 200
    assert avail_res.json()["availability_status"] == "UNAVAILABLE"

    # 3. List educator cases
    educator_cases_res = client.get("/api/educator/cases")
    assert educator_cases_res.status_code == 200
    ed_cases = educator_cases_res.json()
    assert len(ed_cases) >= 1

    # 4. Submit diagnostic details for a case
    diag_res = client.post("/api/cases/CASE-1042/diagnostics", json={
        "diagnostic_details": "Completed CELF-5 standardized battery. Articulation score within average range; mild expressive delay.",
        "educator_name": "Dr. Marcus Vance",
    })
    assert diag_res.status_code == 200
    diag_data = diag_res.json()
    assert "mild expressive delay" in diag_data["diagnostic_details"]

    # Verify timeline event was added
    timeline_events = [e["event_type"] for e in diag_data["timeline"]]
    assert "DIAGNOSTIC_EVALUATION_LOGGED" in timeline_events
