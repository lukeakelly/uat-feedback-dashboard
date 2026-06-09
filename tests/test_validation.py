from services.validation import validate_controlled_value, validate_feedback_item


def test_valid_controlled_value_is_preserved():
    assert validate_controlled_value("severity", "High") == "High"


def test_invalid_controlled_value_becomes_needs_review():
    assert validate_controlled_value("priority", "Do it immediately") == "Needs review"


def test_missing_status_and_decision_use_pending_defaults():
    item = validate_feedback_item({"raw_feedback": "The filter did not work."})
    assert item["status"] == "Pending review"
    assert item["human_decision"] == "Pending"
