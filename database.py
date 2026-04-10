import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "mountains.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT UNIQUE NOT NULL,
            email         TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at    TEXT DEFAULT (datetime('now'))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS climbed_mountains (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            mountain_id TEXT NOT NULL,
            climbed_at  TEXT DEFAULT (datetime('now')),
            notes       TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, mountain_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS goal_mountains (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            mountain_id TEXT NOT NULL,
            added_at    TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, mountain_id)
        )
    """)

    conn.commit()
    conn.close()


# ── Users ─────────────────────────────────────────────────────────────────────

def create_user(username: str, email: str, password_hash: str) -> int:
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_user_by_username(username: str):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_user_by_id(user_id: int):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


# ── Climbed mountains ─────────────────────────────────────────────────────────

def add_climbed(user_id: int, mountain_id: str, notes: str = None) -> bool:
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO climbed_mountains (user_id, mountain_id, notes) VALUES (?, ?, ?)",
            (user_id, mountain_id, notes),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def remove_climbed(user_id: int, mountain_id: str) -> bool:
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM climbed_mountains WHERE user_id = ? AND mountain_id = ?",
            (user_id, mountain_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def get_climbed_ids(user_id: int) -> dict:
    """Returns {mountain_id: {climbed_at, notes}} for the given user."""
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT mountain_id, climbed_at, notes FROM climbed_mountains WHERE user_id = ?",
            (user_id,),
        )
        return {row["mountain_id"]: dict(row) for row in cur.fetchall()}
    finally:
        conn.close()


# ── Goal mountains ────────────────────────────────────────────────────────────

def add_goal(user_id: int, mountain_id: str) -> bool:
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO goal_mountains (user_id, mountain_id) VALUES (?, ?)",
            (user_id, mountain_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def remove_goal(user_id: int, mountain_id: str) -> bool:
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM goal_mountains WHERE user_id = ? AND mountain_id = ?",
            (user_id, mountain_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def get_goal_ids(user_id: int) -> dict:
    """Returns {mountain_id: {added_at}} for the given user."""
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT mountain_id, added_at FROM goal_mountains WHERE user_id = ?",
            (user_id,),
        )
        return {row["mountain_id"]: dict(row) for row in cur.fetchall()}
    finally:
        conn.close()
