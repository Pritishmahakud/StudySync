"""
Database Management Layer for StudySync.
SQLite-backed persistent relational database for users, authentication,
quiz records, active flashcards, learning sessions, and uploaded documents.
"""

from __future__ import annotations

import hashlib
import json
import secrets
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DB_PATH = Path(__file__).parent.parent / "data" / "studysync.db"


def get_db_connection() -> sqlite3.Connection:
    """Get SQLite database connection with row-factory enabled."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Cryptographically secure PBKDF2-HMAC-SHA256 password hashing (100,000 iterations)."""
    if not salt:
        salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000
    ).hex()
    return pw_hash, salt


def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verify submitted password against stored PBKDF2 hash and salt."""
    computed_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(computed_hash, stored_hash)


def init_database():
    """Create all relational tables and seed default data."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 1. Users Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            created_at TEXT NOT NULL,
            last_login TEXT
        );
        """)

        # 2. Learning Sessions Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            subject TEXT NOT NULL,
            concept TEXT NOT NULL,
            minutes INTEGER NOT NULL,
            session_type TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """)

        # 3. Quiz Scores Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            subject TEXT NOT NULL,
            concept TEXT NOT NULL,
            score REAL NOT NULL,
            max_score REAL NOT NULL,
            percent REAL NOT NULL,
            difficulty TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """)

        # 4. Spaced Repetition Flashcards Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS flashcards (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            deck_name TEXT NOT NULL,
            front TEXT NOT NULL,
            back TEXT NOT NULL,
            hint TEXT,
            concept TEXT NOT NULL,
            difficulty TEXT DEFAULT 'medium',
            repetition INTEGER DEFAULT 0,
            interval INTEGER DEFAULT 0,
            easiness_factor REAL DEFAULT 2.5,
            next_review_date TEXT NOT NULL,
            last_reviewed TEXT,
            created_at TEXT NOT NULL
        );
        """)

        # 5. User Uploaded Documents Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            word_count INTEGER DEFAULT 0,
            chunks_count INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        );
        """)

        conn.commit()

        # Seed Default User: Asha (asha@studysync.edu / Password@123)
        cursor.execute("SELECT id FROM users WHERE email = 'asha@studysync.edu'")
        row = cursor.fetchone()
        if not row:
            pw_hash, salt = hash_password("Password@123")
            now_iso = datetime.now(timezone.utc).isoformat()
            cursor.execute(
                "INSERT INTO users (email, name, password_hash, salt, role, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                ("asha@studysync.edu", "Asha Sharma", pw_hash, salt, "student", now_iso)
            )
            asha_id = cursor.lastrowid

            # Seed Historical Quiz Records for Asha
            sample_quizzes = [
                (asha_id, "Maths", "Algebra", 8.0, 10.0, 80.0, "medium", "2026-10-01"),
                (asha_id, "Maths", "Calculus", 4.0, 10.0, 40.0, "hard", "2026-10-01"),
                (asha_id, "Maths", "Calculus", 5.0, 10.0, 50.0, "hard", "2026-10-08"),
                (asha_id, "Maths", "Calculus", 6.0, 10.0, 60.0, "hard", "2026-10-15"),
                (asha_id, "Physics", "Motion", 9.0, 10.0, 90.0, "easy", "2026-10-05"),
                (asha_id, "Physics", "Motion", 8.0, 10.0, 80.0, "medium", "2026-10-12"),
                (asha_id, "Physics", "Thermodynamics", 3.0, 10.0, 30.0, "hard", "2026-10-12"),
                (asha_id, "Physics", "Thermodynamics", 3.0, 10.0, 30.0, "hard", "2026-10-19"),
                (asha_id, "DBMS", "Transactions", 8.0, 10.0, 80.0, "medium", "2026-11-01"),
                (asha_id, "DBMS", "Normalization", 4.0, 10.0, 40.0, "hard", "2026-11-05"),
                (asha_id, "DBMS", "Normalization", 3.5, 10.0, 35.0, "hard", "2026-11-12"),
            ]
            cursor.executemany(
                "INSERT INTO quiz_scores (user_id, subject, concept, score, max_score, percent, difficulty, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                sample_quizzes
            )

            # Seed Default Flashcards for Asha
            today_iso = date.today().isoformat()
            sample_cards = [
                ("fc_dbms_1", asha_id, "DBMS Core", "What is the primary guarantee of ACID Atomicity?",
                 "All operations in the transaction succeed together, or all are completely rolled back with no partial effects.",
                 "All-or-nothing principle", "dbms.transactions.atomicity", "easy", 2, 6, 2.6, today_iso, today_iso, now_iso),
                ("fc_dbms_2", asha_id, "DBMS Core", "State the requirement for a relation schema to be in Boyce-Codd Normal Form (BCNF).",
                 "For every non-trivial functional dependency X -> Y, X must be a superkey of the relation.",
                 "Superkey requirement", "dbms.normalization.bcnf", "hard", 1, 1, 2.3, today_iso, today_iso, now_iso),
                ("fc_os_1", asha_id, "Operating Systems", "What are the four Coffman conditions necessary for deadlock to occur?",
                 "1. Mutual Exclusion, 2. Hold and Wait, 3. No Preemption, 4. Circular Wait.",
                 "Think of resource competition", "os.deadlocks.coffman", "medium", 3, 15, 2.5, today_iso, today_iso, now_iso),
            ]
            cursor.executemany(
                "INSERT INTO flashcards (id, user_id, deck_name, front, back, hint, concept, difficulty, repetition, interval, "
                "easiness_factor, next_review_date, last_reviewed, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                sample_cards
            )

            conn.commit()


# Initialize database on module import
init_database()
