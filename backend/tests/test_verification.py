"""
Tests for action verification logic.
"""
import pytest

from app.agent.verification import verify_action


class TestVerifyAction:
    def test_success_result_is_verified(self):
        result = {"status": "SUCCESS", "message": "Action completed."}
        verification = verify_action(result)
        assert verification["success"] is True
        assert verification["status"] == "VERIFIED"

    def test_simulated_result_is_verified(self):
        result = {"status": "SIMULATED", "message": "Action simulated."}
        verification = verify_action(result)
        assert verification["success"] is True
        assert verification["status"] == "VERIFIED"

    def test_failed_result(self):
        result = {"status": "FAILED", "error": "Specialist not found."}
        verification = verify_action(result)
        assert verification["success"] is False
        assert verification["status"] == "FAILED"
        assert "Specialist not found" in verification["reason"]

    def test_empty_result(self):
        verification = verify_action({})
        assert verification["success"] is False
        assert verification["status"] == "FAILED"

    def test_none_result(self):
        verification = verify_action(None)
        assert verification["success"] is False
        assert verification["status"] == "FAILED"

    def test_success_reason_from_message(self):
        result = {"status": "SUCCESS", "message": "Appointment created."}
        verification = verify_action(result)
        assert "Appointment created" in verification["reason"]

    def test_failure_reason_from_error(self):
        result = {"status": "FAILED", "error": "DB connection error."}
        verification = verify_action(result)
        assert "DB connection error" in verification["reason"]
