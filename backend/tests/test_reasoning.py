"""
Tests for reasoning module — LLM output validation.
"""
import os
import pytest

os.environ["LLM_PROVIDER"] = "mock"

from app.agent.reasoning import (
    _validate_recommendation,
    _mock_recommend,
    recommend_action,
)


class TestMockRecommendations:
    def test_specialist_unavailable_recommends_find_alternative(self):
        bottleneck = {"type": "SPECIALIST_UNAVAILABLE"}
        rec = _mock_recommend(bottleneck)
        assert rec["action"] == "FIND_ALTERNATIVE_SPECIALIST"

    def test_missing_document_recommends_request(self):
        bottleneck = {"type": "MISSING_DOCUMENT"}
        rec = _mock_recommend(bottleneck)
        assert rec["action"] == "REQUEST_DOCUMENT"

    def test_no_specialist_response_recommends_contact(self):
        bottleneck = {"type": "NO_SPECIALIST_RESPONSE"}
        rec = _mock_recommend(bottleneck)
        assert rec["action"] == "CONTACT_SPECIALIST"

    def test_repeated_failure_recommends_escalate(self):
        bottleneck = {"type": "REPEATED_FAILURE"}
        rec = _mock_recommend(bottleneck)
        assert rec["action"] == "ESCALATE_CASE"

    def test_appointment_delayed_recommends_schedule(self):
        bottleneck = {"type": "APPOINTMENT_DELAYED"}
        rec = _mock_recommend(bottleneck)
        assert rec["action"] == "SCHEDULE_FOLLOWUP"

    def test_unknown_bottleneck_returns_followup(self):
        bottleneck = {"type": "UNKNOWN_TYPE"}
        rec = _mock_recommend(bottleneck)
        assert rec["action"] == "SCHEDULE_FOLLOWUP"


class TestValidation:
    def test_valid_recommendation_passes(self):
        rec = {
            "action": "ESCALATE_CASE",
            "reason": "Multiple failures.",
            "evidence": ["Failed 3 times"],
            "confidence": 0.95,
        }
        validated = _validate_recommendation(rec)
        assert validated["action"] == "ESCALATE_CASE"

    def test_invalid_action_raises_value_error(self):
        rec = {
            "action": "DELETE_DATABASE",
            "reason": "...",
            "evidence": [],
            "confidence": 0.9,
        }
        with pytest.raises(ValueError, match="invalid action"):
            _validate_recommendation(rec)

    def test_confidence_clamped_to_range(self):
        rec = {
            "action": "CONTACT_PARENT",
            "reason": "...",
            "evidence": [],
            "confidence": 1.5,   # out of range
        }
        validated = _validate_recommendation(rec)
        assert validated["confidence"] <= 1.0

    def test_evidence_converted_to_list_when_string(self):
        rec = {
            "action": "CONTACT_PARENT",
            "reason": "...",
            "evidence": "Single string evidence",
            "confidence": 0.8,
        }
        validated = _validate_recommendation(rec)
        assert isinstance(validated["evidence"], list)


class TestRecommendAction:
    def test_recommend_action_with_mock_provider(self, minimal_case, empty_timeline):
        bottleneck = {"type": "SPECIALIST_UNAVAILABLE"}
        rec = recommend_action(
            case=minimal_case,
            timeline=empty_timeline,
            bottleneck=bottleneck,
        )
        assert rec["action"] == "FIND_ALTERNATIVE_SPECIALIST"
        assert "reason" in rec
        assert isinstance(rec["evidence"], list)
        assert 0.0 <= rec["confidence"] <= 1.0

    def test_all_mock_actions_are_valid(self, minimal_case, empty_timeline):
        bottleneck_types = [
            "SPECIALIST_UNAVAILABLE",
            "MISSING_DOCUMENT",
            "NO_SPECIALIST_RESPONSE",
            "APPOINTMENT_DELAYED",
            "REPEATED_FAILURE",
        ]
        from app.agent.actions import is_valid_action
        for bt in bottleneck_types:
            rec = recommend_action(
                case=minimal_case,
                timeline=empty_timeline,
                bottleneck={"type": bt},
            )
            assert is_valid_action(rec["action"]), (
                f"Mock returned invalid action '{rec['action']}' for bottleneck '{bt}'"
            )
