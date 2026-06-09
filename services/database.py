from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd

from services.validation import APPROVED_EDITABLE_FIELDS, PENDING_FIELDS

PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = PROJECT_DIR / "data" / "uat_feedback.db"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_db_path() -> Path:
    path = Path(os.getenv("UAT_DB_PATH", str(DEFAULT_DB_PATH)))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


@contextmanager
def connect():
    connection = sqlite3.connect(get_db_path())
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def create_tables() -> None:
    with connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS source_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                uat_round TEXT NOT NULL,
                session_name TEXT NOT NULL,
                source_type TEXT NOT NULL,
                participant_role_default TEXT,
                test_scenario_default TEXT,
                notes TEXT,
                uploaded_at TEXT NOT NULL,
                content_preview TEXT,
                content_text TEXT,
                content_payload TEXT
            );

            CREATE TABLE IF NOT EXISTS pending_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_file_id INTEGER NOT NULL,
                source_location TEXT,
                participant_role TEXT,
                test_scenario TEXT,
                feature_area TEXT,
                raw_feedback TEXT NOT NULL,
                interpreted_issue TEXT,
                type TEXT,
                severity TEXT,
                priority TEXT,
                status TEXT,
                owner TEXT,
                ai_recommendation TEXT,
                human_decision TEXT,
                theme TEXT,
                confidence TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (source_file_id) REFERENCES source_files(id)
            );

            CREATE TABLE IF NOT EXISTS approved_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feedback_id TEXT NOT NULL UNIQUE,
                source_file_id INTEGER NOT NULL,
                uat_round TEXT,
                session_name TEXT,
                source_file TEXT,
                source_location TEXT,
                participant_role TEXT,
                test_scenario TEXT,
                feature_area TEXT,
                raw_feedback TEXT NOT NULL,
                interpreted_issue TEXT,
                type TEXT,
                severity TEXT,
                priority TEXT,
                status TEXT,
                owner TEXT,
                ai_recommendation TEXT,
                human_decision TEXT,
                theme TEXT,
                confidence TEXT,
                notes TEXT,
                devops_reference TEXT,
                archived INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (source_file_id) REFERENCES source_files(id)
            );

            CREATE TABLE IF NOT EXISTS rejected_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_file_id INTEGER NOT NULL,
                source_file TEXT,
                raw_feedback TEXT NOT NULL,
                rejection_reason TEXT,
                rejected_at TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY (source_file_id) REFERENCES source_files(id)
            );

            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id TEXT,
                event_summary TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )


def _audit(
    connection: sqlite3.Connection,
    event_type: str,
    entity_type: str,
    entity_id: object,
    summary: str,
) -> None:
    connection.execute(
        """
        INSERT INTO audit_log (
            event_type, entity_type, entity_id, event_summary, created_at
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (event_type, entity_type, str(entity_id), summary, utc_now()),
    )


def insert_source_file(metadata: dict, content: dict) -> int:
    now = utc_now()
    with connect() as connection:
        cursor = connection.execute(
            """
            INSERT INTO source_files (
                filename, file_type, uat_round, session_name, source_type,
                participant_role_default, test_scenario_default, notes,
                uploaded_at, content_preview, content_text, content_payload
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                metadata["filename"],
                metadata["file_type"],
                metadata["uat_round"],
                metadata["session_name"],
                metadata["source_type"],
                metadata.get("participant_role_default", ""),
                metadata.get("test_scenario_default", ""),
                metadata.get("notes", ""),
                now,
                content.get("preview", ""),
                content.get("text", ""),
                json.dumps(content.get("records", []), ensure_ascii=False),
            ),
        )
        source_id = int(cursor.lastrowid)
        _audit(connection, "uploaded", "source_file", source_id, f"Uploaded {metadata['filename']}")
        return source_id


def get_source_file(source_file_id: int) -> dict | None:
    with connect() as connection:
        row = connection.execute(
            "SELECT * FROM source_files WHERE id = ?", (source_file_id,)
        ).fetchone()
    if row is None:
        return None
    result = dict(row)
    result["records"] = json.loads(result.pop("content_payload") or "[]")
    return result


def list_source_files() -> pd.DataFrame:
    with connect() as connection:
        return pd.read_sql_query(
            """
            SELECT id, filename, uat_round, session_name, source_type, uploaded_at
            FROM source_files
            ORDER BY id DESC
            """,
            connection,
        )


def insert_pending_feedback(source_file_id: int, items: Iterable[dict]) -> int:
    rows = list(items)
    if not rows:
        return 0
    now = utc_now()
    columns = ", ".join(PENDING_FIELDS)
    placeholders = ", ".join("?" for _ in PENDING_FIELDS)
    with connect() as connection:
        for item in rows:
            values = [item.get(field, "") for field in PENDING_FIELDS]
            connection.execute(
                f"""
                INSERT INTO pending_feedback (
                    source_file_id, {columns}, created_at, updated_at
                ) VALUES (?, {placeholders}, ?, ?)
                """,
                [source_file_id, *values, now, now],
            )
        _audit(
            connection,
            "extracted",
            "source_file",
            source_file_id,
            f"Created {len(rows)} pending feedback item(s)",
        )
    return len(rows)


def load_pending_feedback() -> pd.DataFrame:
    with connect() as connection:
        return pd.read_sql_query(
            """
            SELECT p.*, s.filename AS source_file, s.uat_round, s.session_name
            FROM pending_feedback p
            JOIN source_files s ON s.id = p.source_file_id
            ORDER BY p.id
            """,
            connection,
        )


def update_pending_feedback(records: Iterable[dict]) -> int:
    rows = list(records)
    if not rows:
        return 0
    assignments = ", ".join(f"{field} = ?" for field in PENDING_FIELDS)
    now = utc_now()
    with connect() as connection:
        for row in rows:
            connection.execute(
                f"UPDATE pending_feedback SET {assignments}, updated_at = ? WHERE id = ?",
                [*(row.get(field, "") for field in PENDING_FIELDS), now, int(row["id"])],
            )
    return len(rows)


def _next_feedback_number(connection: sqlite3.Connection) -> int:
    row = connection.execute(
        """
        SELECT MAX(CAST(SUBSTR(feedback_id, 5) AS INTEGER)) AS maximum
        FROM approved_feedback
        WHERE feedback_id LIKE 'UAT-%'
        """
    ).fetchone()
    return int(row["maximum"] or 0) + 1


def approve_pending_feedback(pending_ids: Iterable[int]) -> list[str]:
    ids = [int(value) for value in pending_ids]
    approved_ids: list[str] = []
    if not ids:
        return approved_ids

    now = utc_now()
    with connect() as connection:
        next_number = _next_feedback_number(connection)
        for pending_id in ids:
            row = connection.execute(
                """
                SELECT p.*, s.filename AS source_file, s.uat_round, s.session_name
                FROM pending_feedback p
                JOIN source_files s ON s.id = p.source_file_id
                WHERE p.id = ?
                """,
                (pending_id,),
            ).fetchone()
            if row is None:
                continue

            feedback_id = f"UAT-{next_number:04d}"
            next_number += 1
            decision = row["human_decision"]
            if decision in ("", "Pending", "Needs review"):
                decision = "Accepted"
            connection.execute(
                """
                INSERT INTO approved_feedback (
                    feedback_id, source_file_id, uat_round, session_name, source_file,
                    source_location, participant_role, test_scenario, feature_area,
                    raw_feedback, interpreted_issue, type, severity, priority, status,
                    owner, ai_recommendation, human_decision, theme, confidence, notes,
                    devops_reference, archived, created_at, updated_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    '', 0, ?, ?
                )
                """,
                (
                    feedback_id,
                    row["source_file_id"],
                    row["uat_round"],
                    row["session_name"],
                    row["source_file"],
                    row["source_location"],
                    row["participant_role"],
                    row["test_scenario"],
                    row["feature_area"],
                    row["raw_feedback"],
                    row["interpreted_issue"],
                    row["type"],
                    row["severity"],
                    row["priority"],
                    row["status"],
                    row["owner"],
                    row["ai_recommendation"],
                    decision,
                    row["theme"],
                    row["confidence"],
                    row["notes"],
                    now,
                    now,
                ),
            )
            connection.execute("DELETE FROM pending_feedback WHERE id = ?", (pending_id,))
            _audit(
                connection,
                "approved",
                "feedback",
                feedback_id,
                f"Approved pending feedback item {pending_id}",
            )
            approved_ids.append(feedback_id)
    return approved_ids


def reject_pending_feedback(
    pending_ids: Iterable[int], rejection_reason: str = "Rejected during human review"
) -> int:
    ids = [int(value) for value in pending_ids]
    if not ids:
        return 0
    now = utc_now()
    count = 0
    with connect() as connection:
        for pending_id in ids:
            row = connection.execute(
                """
                SELECT p.*, s.filename AS source_file
                FROM pending_feedback p
                JOIN source_files s ON s.id = p.source_file_id
                WHERE p.id = ?
                """,
                (pending_id,),
            ).fetchone()
            if row is None:
                continue
            connection.execute(
                """
                INSERT INTO rejected_feedback (
                    source_file_id, source_file, raw_feedback,
                    rejection_reason, rejected_at, notes
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    row["source_file_id"],
                    row["source_file"],
                    row["raw_feedback"],
                    rejection_reason,
                    now,
                    row["notes"],
                ),
            )
            connection.execute("DELETE FROM pending_feedback WHERE id = ?", (pending_id,))
            _audit(
                connection,
                "rejected",
                "pending_feedback",
                pending_id,
                rejection_reason,
            )
            count += 1
    return count


def load_approved_feedback(include_archived: bool = False) -> pd.DataFrame:
    where = "" if include_archived else "WHERE archived = 0"
    with connect() as connection:
        return pd.read_sql_query(
            f"SELECT * FROM approved_feedback {where} ORDER BY id",
            connection,
        )


def update_approved_feedback(records: Iterable[dict]) -> int:
    rows = list(records)
    if not rows:
        return 0
    assignments = ", ".join(f"{field} = ?" for field in APPROVED_EDITABLE_FIELDS)
    now = utc_now()
    with connect() as connection:
        for row in rows:
            connection.execute(
                f"UPDATE approved_feedback SET {assignments}, updated_at = ? WHERE id = ?",
                [
                    *(row.get(field, "") for field in APPROVED_EDITABLE_FIELDS),
                    now,
                    int(row["id"]),
                ],
            )
            _audit(
                connection,
                "updated",
                "feedback",
                row.get("feedback_id", row["id"]),
                "Updated approved feedback item",
            )
    return len(rows)


def archive_approved_feedback(row_ids: Iterable[int]) -> int:
    ids = [int(value) for value in row_ids]
    now = utc_now()
    with connect() as connection:
        for row_id in ids:
            connection.execute(
                """
                UPDATE approved_feedback
                SET archived = 1, status = 'Archived', updated_at = ?
                WHERE id = ?
                """,
                (now, row_id),
            )
            _audit(connection, "archived", "feedback", row_id, "Archived approved feedback item")
    return len(ids)


def load_rejected_feedback() -> pd.DataFrame:
    with connect() as connection:
        return pd.read_sql_query(
            "SELECT * FROM rejected_feedback ORDER BY id",
            connection,
        )


def load_audit_log() -> pd.DataFrame:
    with connect() as connection:
        return pd.read_sql_query(
            "SELECT * FROM audit_log ORDER BY id DESC",
            connection,
        )
