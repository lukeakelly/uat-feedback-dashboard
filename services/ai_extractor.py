from __future__ import annotations

import json
import os
import re

from dotenv import load_dotenv

from services.validation import (
    FEATURE_AREAS,
    FEEDBACK_TYPES,
    HUMAN_DECISIONS,
    OWNERS,
    PRIORITIES,
    SEVERITIES,
    STATUSES,
    validate_feedback_item,
)

load_dotenv()


def ai_is_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def _prompt(content: str | dict, metadata: dict) -> str:
    if isinstance(content, dict) and content.get("records"):
        source_content = json.dumps(content["records"], ensure_ascii=False, indent=2)
        content_note = (
            "The feedback content is a JSON list of source_location and raw_feedback "
            "records. Copy raw_feedback without the source-location label."
        )
    elif isinstance(content, dict):
        source_content = str(content.get("text", ""))
        content_note = "The feedback content is plain text."
    else:
        source_content = content
        content_note = "The feedback content is plain text."

    return f"""
You are analysing UAT feedback for an AI Library application.

Extract each distinct item of feedback into a structured register.

Rules:
- Preserve the original feedback exactly in raw_feedback.
- Create one row per distinct item.
- Do not combine unrelated issues.
- Do not invent missing facts.
- If unclear, use Needs review.
- Classify each item using the supplied controlled values only.
- Severity should reflect user impact.
- Priority should reflect likely delivery treatment.
- Human decision must default to Pending.
- Status must default to Pending review.
- Return valid JSON only.
- Do not include commentary outside JSON.

Controlled values:
feature_area: {FEATURE_AREAS}
type: {FEEDBACK_TYPES}
severity: {SEVERITIES}
priority: {PRIORITIES}
status: {STATUSES}
owner: {OWNERS}
human_decision: {HUMAN_DECISIONS}

Source metadata:
UAT round: {metadata.get("uat_round", "")}
Session name: {metadata.get("session_name", "")}
Default participant role: {metadata.get("participant_role_default", "")}
Default test scenario: {metadata.get("test_scenario_default", "")}

Expected JSON shape:
[
  {{
    "source_location": "",
    "participant_role": "",
    "test_scenario": "",
    "feature_area": "",
    "raw_feedback": "",
    "interpreted_issue": "",
    "type": "",
    "severity": "",
    "priority": "",
    "status": "Pending review",
    "owner": "",
    "ai_recommendation": "",
    "human_decision": "Pending",
    "theme": "",
    "confidence": "",
    "notes": ""
  }}
]

Feedback content:
{content_note}
{source_content}
""".strip()


def _parse_json(text: str) -> list[dict]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    result = json.loads(cleaned)
    if not isinstance(result, list):
        raise ValueError("AI extraction did not return a JSON list.")
    return result


def extract_with_ai(content: str | dict, metadata: dict) -> list[dict]:
    if not ai_is_available():
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    from openai import OpenAI

    client = OpenAI()
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
        input=_prompt(content, metadata),
    )
    items = _parse_json(response.output_text)
    return [validate_feedback_item(item) for item in items]
