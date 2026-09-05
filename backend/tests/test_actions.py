"""
Tests for action validation.
"""
import pytest

from app.agent.actions import ActionType, ALLOWED_ACTIONS, is_valid_action


class TestActionType:
    def test_all_allowed_actions_are_valid(self):
        for action in ActionType:
            assert is_valid_action(action.value), f"{action.value} should be valid"

    def test_invalid_action_strings(self):
        invalid = [
            "DELETE_CASE",
            "SEND_EMAIL",
            "MODIFY_DATABASE",
            "RUN_PYTHON",
            "",
            "contact_parent",   # wrong case
            "CONTACT_PARENT_AND_SPECIALIST",
        ]
        for action in invalid:
            assert not is_valid_action(action), f"{action} should be invalid"

    def test_allowed_actions_set_matches_enum(self):
        assert {a.value for a in ALLOWED_ACTIONS} == {a.value for a in ActionType}

    @pytest.mark.parametrize("action", [
        "CONTACT_PARENT",
        "REQUEST_DOCUMENT",
        "CONTACT_SPECIALIST",
        "FIND_ALTERNATIVE_SPECIALIST",
        "SCHEDULE_FOLLOWUP",
        "ESCALATE_CASE",
    ])
    def test_each_allowed_action(self, action: str):
        assert is_valid_action(action)
