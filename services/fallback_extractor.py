from __future__ import annotations

from services.validation import validate_feedback_item


def extract_fallback(content: dict, metadata: dict | None = None) -> list[dict]:
    metadata = metadata or {}
    records = content.get("records") or []
    if not records:
        records = [
            {"source_location": f"Line {number}", "raw_feedback": line}
            for number, line in enumerate(content.get("text", "").splitlines(), start=1)
            if line.strip()
        ]

    items = []
    for record in records:
        raw_feedback = str(record.get("raw_feedback", ""))
        if not raw_feedback.strip():
            continue
        item = {
            "source_location": record.get("source_location", ""),
            "participant_role": metadata.get("participant_role_default", ""),
            "test_scenario": metadata.get("test_scenario_default", ""),
            "feature_area": "Needs review",
            "raw_feedback": raw_feedback,
            "interpreted_issue": raw_feedback,
            "type": "Needs review",
            "severity": "Needs review",
            "priority": "Needs review",
            "status": "Pending review",
            "owner": "Needs review",
            "ai_recommendation": "",
            "human_decision": "Pending",
            "theme": "Needs review",
            "confidence": "Low",
            "notes": "",
        }
        items.append(validate_feedback_item(item))
    return items
