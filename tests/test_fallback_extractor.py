from services.fallback_extractor import extract_fallback


def test_fallback_extracts_one_item_per_non_empty_line():
    content = {
        "text": "First issue\n\nSecond issue",
        "records": [
            {"source_location": "Line 1", "raw_feedback": "First issue"},
            {"source_location": "Line 3", "raw_feedback": "Second issue"},
        ],
    }

    items = extract_fallback(
        content,
        {
            "participant_role_default": "Tester",
            "test_scenario_default": "Search",
        },
    )

    assert len(items) == 2
    assert items[0]["raw_feedback"] == "First issue"
    assert items[0]["participant_role"] == "Tester"
    assert items[0]["type"] == "Needs review"
    assert items[0]["status"] == "Pending review"
    assert items[0]["human_decision"] == "Pending"
