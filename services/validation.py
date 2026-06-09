from __future__ import annotations

FEATURE_AREAS = [
    "Home",
    "Search",
    "Filtering",
    "Record detail",
    "Submit a record",
    "Edit a record",
    "Approval workflow",
    "My items",
    "Admin",
    "Content quality",
    "Accessibility",
    "Security / permissions",
    "Performance",
    "Notifications",
    "Reporting",
    "Other",
    "Needs review",
]

FEEDBACK_TYPES = [
    "Defect",
    "UX",
    "Content",
    "Accessibility",
    "Search / relevance",
    "Workflow",
    "Security / permissions",
    "Performance",
    "Data / metadata",
    "Training / guidance",
    "Enhancement request",
    "Out of scope",
    "Needs review",
]

SEVERITIES = ["Blocker", "High", "Medium", "Low", "Needs review"]

PRIORITIES = [
    "Must fix before UAT exit",
    "Must fix before go-live",
    "Should fix",
    "Could fix",
    "Backlog",
    "No action",
    "Needs review",
]

STATUSES = [
    "Pending review",
    "New",
    "Triaged",
    "In progress",
    "Resolved",
    "Retest required",
    "Closed",
    "Deferred",
    "Archived",
]

OWNERS = [
    "Product",
    "UX",
    "Front-end",
    "Back-end",
    "Search",
    "Content",
    "Accessibility",
    "Security",
    "Delivery",
    "Client decision",
    "Training / change",
    "Needs review",
]

HUMAN_DECISIONS = [
    "Pending",
    "Accepted",
    "Rejected",
    "Duplicate",
    "Deferred",
    "Needs clarification",
]

UAT_ROUNDS = [
    "Internal UAT",
    "Client UAT",
    "Regression UAT",
    "Accessibility review",
    "Security review",
    "Other",
]

SOURCE_TYPES = [
    "Word document",
    "Excel workbook",
    "CSV export",
    "Meeting notes",
    "Tester notes",
    "Other",
]

CONTROLLED_FIELDS = {
    "feature_area": FEATURE_AREAS,
    "type": FEEDBACK_TYPES,
    "severity": SEVERITIES,
    "priority": PRIORITIES,
    "status": STATUSES,
    "owner": OWNERS,
    "human_decision": HUMAN_DECISIONS,
}

PENDING_FIELDS = [
    "source_location",
    "participant_role",
    "test_scenario",
    "feature_area",
    "raw_feedback",
    "interpreted_issue",
    "type",
    "severity",
    "priority",
    "status",
    "owner",
    "ai_recommendation",
    "human_decision",
    "theme",
    "confidence",
    "notes",
]

APPROVED_EDITABLE_FIELDS = [
    "uat_round",
    "session_name",
    "source_location",
    "participant_role",
    "test_scenario",
    "feature_area",
    "raw_feedback",
    "interpreted_issue",
    "type",
    "severity",
    "priority",
    "status",
    "owner",
    "ai_recommendation",
    "human_decision",
    "theme",
    "confidence",
    "notes",
    "devops_reference",
]

OPEN_STATUSES = [
    "New",
    "Triaged",
    "In progress",
    "Retest required",
    "Deferred",
    "Pending review",
]
RESOLVED_STATUSES = ["Resolved", "Closed"]
MUST_FIX_PRIORITIES = ["Must fix before UAT exit", "Must fix before go-live"]


def validate_controlled_value(field: str, value: object) -> str:
    options = CONTROLLED_FIELDS[field]
    text = "" if value is None else str(value).strip()
    return text if text in options else "Needs review"


def validate_feedback_item(item: dict) -> dict:
    validated = {field: "" if item.get(field) is None else str(item.get(field)) for field in PENDING_FIELDS}
    for field in CONTROLLED_FIELDS:
        validated[field] = validate_controlled_value(field, item.get(field))
    validated["status"] = (
        validated["status"] if validated["status"] in STATUSES else "Pending review"
    )
    validated["human_decision"] = (
        validated["human_decision"]
        if validated["human_decision"] in HUMAN_DECISIONS
        else "Pending"
    )
    if not validated["raw_feedback"].strip():
        raise ValueError("A feedback item must include raw feedback.")
    return validated
