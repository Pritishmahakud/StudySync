"""Contextual memory: SQLite store for profile, plans and progress events."""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

DB = Path(__file__).parent.parent / "data" / "studyplanner.db"


def _c():
    DB.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(str(DB))
    c.execute("CREATE TABLE IF NOT EXISTS profile(student_id TEXT PRIMARY KEY, data TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS plans(id INTEGER PRIMARY KEY, student_id TEXT, ts REAL, data TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, student_id TEXT, ts REAL, kind TEXT, data TEXT)")
    return c


def save_profile(student_id: str, data: dict):
    with _c() as c:
        c.execute("REPLACE INTO profile VALUES (?,?)", (student_id, json.dumps(data, default=str)))


def load_profile(student_id: str) -> dict | None:
    with _c() as c:
        r = c.execute("SELECT data FROM profile WHERE student_id=?", (student_id,)).fetchone()
    return json.loads(r[0]) if r else None


def save_plan(student_id: str, plan: dict):
    with _c() as c:
        c.execute("INSERT INTO plans(student_id,ts,data) VALUES (?,?,?)",
                  (student_id, time.time(), json.dumps(plan, default=str)))


def latest_plan(student_id: str) -> dict | None:
    with _c() as c:
        r = c.execute("SELECT data FROM plans WHERE student_id=? ORDER BY id DESC LIMIT 1", (student_id,)).fetchone()
    return json.loads(r[0]) if r else None


def log_event(student_id: str, kind: str, data: dict):
    with _c() as c:
        c.execute("INSERT INTO events(student_id,ts,kind,data) VALUES (?,?,?,?)",
                  (student_id, time.time(), kind, json.dumps(data, default=str)))


def events(student_id: str) -> list[dict]:
    with _c() as c:
        rows = c.execute("SELECT ts,kind,data FROM events WHERE student_id=? ORDER BY id", (student_id,)).fetchall()
    return [{"ts": r[0], "kind": r[1], **json.loads(r[2])} for r in rows]
