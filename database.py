import sqlite3
import json
from pathlib import Path
from datetime import datetime


# Database file location
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "agentverse.db"


def get_connection():
    """Create a connection to the SQLite database."""

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=10,
    )
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create and update the research history table."""

    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS research_history (
                id TEXT PRIMARY KEY,
                question TEXT NOT NULL,
                report TEXT NOT NULL,
                collection TEXT NOT NULL DEFAULT 'General',
                created_at TEXT NOT NULL,
                agent_status TEXT NOT NULL DEFAULT '{}'
            )
            """
        )

        # Update an existing database without deleting old reports.
        columns = connection.execute(
            "PRAGMA table_info(research_history)"
        ).fetchall()

        column_names = [column["name"] for column in columns]

        if "agent_status" not in column_names:
            connection.execute(
                """
                ALTER TABLE research_history
                ADD COLUMN agent_status TEXT NOT NULL DEFAULT '{}'
                """
            )


def save_research(
    report_id: str,
    question: str,
    report: str,
    collection: str = "General",
    agent_status: dict | None = None,
) -> None:
    """Save a completed research report and its agent statuses."""

    created_at = datetime.now().isoformat(timespec="seconds")

    status_json = json.dumps(
        agent_status or {},
        ensure_ascii=False,
    )

    with get_connection() as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO research_history
            (
                id,
                question,
                report,
                collection,
                created_at,
                agent_status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                report_id,
                question.strip(),
                report,
                collection.strip() or "General",
                created_at,
                status_json,
            ),
        )


def get_all_research() -> list[dict]:
    """Return saved reports, newest first."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                question,
                report,
                collection,
                created_at,
                agent_status
            FROM research_history
            ORDER BY created_at DESC
            """
        ).fetchall()

    research_list = []

    for row in rows:
        item = dict(row)

        try:
            item["agent_status"] = json.loads(
                item.get("agent_status") or "{}"
            )
        except (json.JSONDecodeError, TypeError):
            item["agent_status"] = {}

        research_list.append(item)

    return research_list


def get_research_by_id(report_id: str):
    """Retrieve one report and its agent statuses by ID."""

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                question,
                report,
                collection,
                created_at,
                agent_status
            FROM research_history
            WHERE id = ?
            """,
            (report_id,),
        ).fetchone()

    if not row:
        return None

    item = dict(row)

    try:
        item["agent_status"] = json.loads(
            item.get("agent_status") or "{}"
        )
    except (json.JSONDecodeError, TypeError):
        item["agent_status"] = {}

    return item


def delete_research(report_id: str) -> bool:
    """Delete a saved report."""

    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM research_history
            WHERE id = ?
            """,
            (report_id,),
        )

        return cursor.rowcount > 0


def get_collections() -> list[str]:
    """Return the saved collection names."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT DISTINCT collection
            FROM research_history
            ORDER BY collection
            """
        ).fetchall()

    return [row["collection"] for row in rows]


def update_research_collection(
    report_id: str,
    collection: str,
) -> bool:
    """Update the collection assigned to a saved report."""

    collection = collection.strip() or "General"

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE research_history
            SET collection = ?
            WHERE id = ?
            """,
            (collection, report_id),
        )

        return cursor.rowcount > 0


# Initialize the database when this module is imported.
initialize_database()