from services.database import (
    approve_pending_feedback,
    create_tables,
    get_db_path,
    insert_pending_feedback,
    insert_source_file,
    load_approved_feedback,
    load_pending_feedback,
)
from services.fallback_extractor import extract_fallback


def test_database_creation_and_approval(tmp_path, monkeypatch):
    database_path = tmp_path / "test.db"
    monkeypatch.setenv("UAT_DB_PATH", str(database_path))
    create_tables()

    content = {
        "text": "Search returned no results.",
        "records": [
            {
                "source_location": "Line 1",
                "raw_feedback": "Search returned no results.",
            }
        ],
        "preview": "Search returned no results.",
    }
    metadata = {
        "filename": "feedback.txt",
        "file_type": "txt",
        "uat_round": "Internal UAT",
        "session_name": "Search test",
        "source_type": "Tester notes",
        "participant_role_default": "Tester",
        "test_scenario_default": "Search",
        "notes": "",
    }
    source_id = insert_source_file(metadata, content)
    items = extract_fallback(content, metadata)
    assert insert_pending_feedback(source_id, items) == 1

    pending = load_pending_feedback()
    feedback_ids = approve_pending_feedback([int(pending.iloc[0]["id"])])

    assert get_db_path() == database_path
    assert feedback_ids == ["UAT-0001"]
    assert load_pending_feedback().empty
    approved = load_approved_feedback()
    assert len(approved) == 1
    assert approved.iloc[0]["raw_feedback"] == "Search returned no results."
    assert approved.iloc[0]["human_decision"] == "Accepted"
