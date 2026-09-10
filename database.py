import sqlite3
from datetime import datetime, timedelta
from contextlib import contextmanager

from config import DB_PATH, LOBBY_COOLDOWN_MINUTES


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_conn():
    conn = _connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT,
                faceit_nickname TEXT,
                faceit_id TEXT,
                level INTEGER,
                elo INTEGER,
                role TEXT,
                has_mic INTEGER DEFAULT 1,
                is_blocked INTEGER DEFAULT 0,
                created_at TEXT,
                updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS lobbies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                level_min INTEGER,
                level_max INTEGER,
                role_needed TEXT,
                mic_required INTEGER DEFAULT 0,
                comment TEXT,
                chat_id TEXT,
                message_id INTEGER,
                status TEXT DEFAULT 'active',
                created_at TEXT,
                FOREIGN KEY (owner_id) REFERENCES users(telegram_id)
            );

            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reporter_id INTEGER NOT NULL,
                reported_id INTEGER NOT NULL,
                reason TEXT,
                created_at TEXT
            );
            """
        )


# ---------- USERS ----------

def upsert_user(telegram_id: int, username: str, faceit_nickname: str,
                 faceit_id: str, level: int, elo: int):
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT telegram_id FROM users WHERE telegram_id = ?", (telegram_id,)
        ).fetchone()
        if existing:
            conn.execute(
                """UPDATE users SET username=?, faceit_nickname=?, faceit_id=?,
                   level=?, elo=?, updated_at=? WHERE telegram_id=?""",
                (username, faceit_nickname, faceit_id, level, elo, now, telegram_id),
            )
        else:
            conn.execute(
                """INSERT INTO users (telegram_id, username, faceit_nickname, faceit_id,
                   level, elo, role, has_mic, is_blocked, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, NULL, 1, 0, ?, ?)""",
                (telegram_id, username, faceit_nickname, faceit_id, level, elo, now, now),
            )


def get_user(telegram_id: int):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        ).fetchone()
        return dict(row) if row else None


def set_role(telegram_id: int, role: str):
    with get_conn() as conn:
        conn.execute("UPDATE users SET role=? WHERE telegram_id=?", (role, telegram_id))


def set_mic(telegram_id: int, has_mic: bool):
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET has_mic=? WHERE telegram_id=?", (int(has_mic), telegram_id)
        )


def is_blocked(telegram_id: int) -> bool:
    user = get_user(telegram_id)
    return bool(user and user["is_blocked"])


def block_user(telegram_id: int):
    with get_conn() as conn:
        conn.execute("UPDATE users SET is_blocked=1 WHERE telegram_id=?", (telegram_id,))


def unblock_user(telegram_id: int):
    with get_conn() as conn:
        conn.execute("UPDATE users SET is_blocked=0 WHERE telegram_id=?", (telegram_id,))


# ---------- LOBBIES ----------

def can_create_lobby(telegram_id: int) -> bool:
    cutoff = (datetime.utcnow() - timedelta(minutes=LOBBY_COOLDOWN_MINUTES)).isoformat()
    with get_conn() as conn:
        row = conn.execute(
            """SELECT id FROM lobbies WHERE owner_id=? AND created_at > ?
               ORDER BY created_at DESC LIMIT 1""",
            (telegram_id, cutoff),
        ).fetchone()
        return row is None


def get_active_lobby_by_user(telegram_id: int):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM lobbies WHERE owner_id=? AND status='active' "
            "ORDER BY created_at DESC LIMIT 1",
            (telegram_id,),
        ).fetchone()
        return dict(row) if row else None


def create_lobby(owner_id: int, level_min: int, level_max: int, role_needed: str,
                  mic_required: bool, comment: str = "") -> int:
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO lobbies (owner_id, level_min, level_max, role_needed,
               mic_required, comment, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, 'active', ?)""",
            (owner_id, level_min, level_max, role_needed, int(mic_required), comment, now),
        )
        return cur.lastrowid


def set_lobby_message(lobby_id: int, chat_id: str, message_id: int):
    with get_conn() as conn:
        conn.execute(
            "UPDATE lobbies SET chat_id=?, message_id=? WHERE id=?",
            (chat_id, message_id, lobby_id),
        )


def get_lobby(lobby_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM lobbies WHERE id=?", (lobby_id,)).fetchone()
        return dict(row) if row else None


def close_lobby(lobby_id: int):
    with get_conn() as conn:
        conn.execute("UPDATE lobbies SET status='closed' WHERE id=?", (lobby_id,))


# ---------- REPORTS ----------

def add_report(reporter_id: int, reported_id: int, reason: str):
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO reports (reporter_id, reported_id, reason, created_at)
               VALUES (?, ?, ?, ?)""",
            (reporter_id, reported_id, reason, now),
        )


def get_reports(limit: int = 20):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM reports ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]
