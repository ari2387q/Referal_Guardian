from enum import Enum


class ActionType(str, Enum):
    CONTACT_PARENT = "CONTACT_PARENT"
    REQUEST_DOCUMENT = "REQUEST_DOCUMENT"
    CONTACT_SPECIALIST = "CONTACT_SPECIALIST"
    FIND_ALTERNATIVE_SPECIALIST = "FIND_ALTERNATIVE_SPECIALIST"
    SCHEDULE_FOLLOWUP = "SCHEDULE_FOLLOWUP"
    ESCALATE_CASE = "ESCALATE_CASE"


ALLOWED_ACTIONS = {
    ActionType.CONTACT_PARENT,
    ActionType.REQUEST_DOCUMENT,
    ActionType.CONTACT_SPECIALIST,
    ActionType.FIND_ALTERNATIVE_SPECIALIST,
    ActionType.SCHEDULE_FOLLOWUP,
    ActionType.ESCALATE_CASE,
}


def is_valid_action(action: str) -> bool:
    """
    Check whether an action is part of the controlled action set.
    """

    try:
        action_type = ActionType(action)
    except ValueError:
        return False

    return action_type in ALLOWED_ACTIONS
