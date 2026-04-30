"""SQLite database for storing generated CPG ideas."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).parent.parent / "ideas.db"


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ideas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            category TEXT NOT NULL,
            brand_name TEXT NOT NULL,
            tagline TEXT NOT NULL,
            product_type TEXT NOT NULL,
            target_audience TEXT NOT NULL,
            reasoning TEXT NOT NULL,
            trends_data TEXT NOT NULL,
            trend_keywords TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_idea(idea: dict[str, Any]) -> int:
    conn = get_db()
    cursor = conn.execute(
        """INSERT INTO ideas (created_at, category, brand_name, tagline, product_type,
           target_audience, reasoning, trends_data, trend_keywords)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            idea["created_at"],
            idea["category"],
            idea["brand_name"],
            idea["tagline"],
            idea["product_type"],
            idea["target_audience"],
            idea["reasoning"],
            json.dumps(idea["trends_data"]),
            json.dumps(idea["trend_keywords"]),
        ),
    )
    conn.commit()
    idea_id = cursor.lastrowid
    conn.close()
    return idea_id


def get_latest_ideas(limit: int = 20) -> list[dict[str, Any]]:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM ideas ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_todays_ideas() -> list[dict[str, Any]]:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM ideas WHERE created_at LIKE ? ORDER BY created_at DESC",
        (f"{today}%",),
    ).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row)
    d["trends_data"] = json.loads(d["trends_data"])
    d["trend_keywords"] = json.loads(d["trend_keywords"])
    return d
