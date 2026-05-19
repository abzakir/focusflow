"""Database manager for FocusFlow - handles all SQLite operations."""
import sqlite3
import os
from datetime import datetime, date


class DatabaseManager:
    """Manages all database operations for FocusFlow."""

    def __init__(self, db_path=None):
        if db_path is None:
            app_data = os.path.join(os.getenv('APPDATA', '.'), 'FocusFlow')
            os.makedirs(app_data, exist_ok=True)
            db_path = os.path.join(app_data, 'focusflow.db')
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._init_schema()

    def _connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")

    def _init_schema(self):
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                self.conn.executescript(f.read())
        else:
            self.conn.executescript(self._inline_schema())
        self.conn.commit()

    def _inline_schema(self):
        return """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,
            duration_minutes REAL DEFAULT 0,
            session_type TEXT DEFAULT 'focus'
        );
        CREATE TABLE IF NOT EXISTS daily_goals (
            date TEXT PRIMARY KEY,
            goal_minutes INTEGER DEFAULT 120,
            completed_minutes REAL DEFAULT 0,
            status TEXT DEFAULT 'pending'
        );
        CREATE TABLE IF NOT EXISTS streak (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            last_completed_date TEXT
        );
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            reminder_sent INTEGER DEFAULT 0,
            delay_minutes REAL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        INSERT OR IGNORE INTO streak (id, current_streak, longest_streak) VALUES (1, 0, 0);
        """

    # ── Session Methods ──
    def start_session(self, session_type='focus'):
        now = datetime.now()
        cur = self.conn.execute(
            "INSERT INTO sessions (date, start_time, session_type) VALUES (?, ?, ?)",
            (now.strftime('%Y-%m-%d'), now.strftime('%Y-%m-%d %H:%M:%S'), session_type)
        )
        self.conn.commit()
        return cur.lastrowid

    def end_session(self, session_id, duration_minutes):
        now = datetime.now()
        self.conn.execute(
            "UPDATE sessions SET end_time=?, duration_minutes=? WHERE id=?",
            (now.strftime('%Y-%m-%d %H:%M:%S'), duration_minutes, session_id)
        )
        self.conn.commit()

    def get_sessions_for_date(self, target_date=None):
        if target_date is None:
            target_date = date.today().strftime('%Y-%m-%d')
        rows = self.conn.execute(
            "SELECT * FROM sessions WHERE date=? ORDER BY start_time", (target_date,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_sessions_range(self, start_date, end_date):
        rows = self.conn.execute(
            "SELECT date, SUM(duration_minutes) as total_minutes FROM sessions "
            "WHERE date BETWEEN ? AND ? AND session_type='focus' GROUP BY date ORDER BY date",
            (start_date, end_date)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_total_minutes_today(self):
        today = date.today().strftime('%Y-%m-%d')
        row = self.conn.execute(
            "SELECT COALESCE(SUM(duration_minutes), 0) as total FROM sessions "
            "WHERE date=? AND session_type='focus'", (today,)
        ).fetchone()
        return row['total'] if row else 0

    def get_total_sessions(self):
        row = self.conn.execute(
            "SELECT COUNT(*) as cnt FROM sessions WHERE session_type='focus' AND duration_minutes > 0"
        ).fetchone()
        return row['cnt'] if row else 0

    def get_total_focus_hours(self):
        row = self.conn.execute(
            "SELECT COALESCE(SUM(duration_minutes), 0) as total FROM sessions WHERE session_type='focus'"
        ).fetchone()
        return (row['total'] / 60.0) if row else 0

    # ── Daily Goal Methods ──
    def get_or_create_daily_goal(self, target_date=None, default_goal=120):
        if target_date is None:
            target_date = date.today().strftime('%Y-%m-%d')
        row = self.conn.execute(
            "SELECT * FROM daily_goals WHERE date=?", (target_date,)
        ).fetchone()
        if row is None:
            self.conn.execute(
                "INSERT INTO daily_goals (date, goal_minutes) VALUES (?, ?)",
                (target_date, default_goal)
            )
            self.conn.commit()
            row = self.conn.execute(
                "SELECT * FROM daily_goals WHERE date=?", (target_date,)
            ).fetchone()
        return dict(row)

    def update_daily_completed(self, minutes, target_date=None):
        if target_date is None:
            target_date = date.today().strftime('%Y-%m-%d')
        self.get_or_create_daily_goal(target_date)
        total = self.get_total_minutes_today()
        goal = self.conn.execute(
            "SELECT goal_minutes FROM daily_goals WHERE date=?", (target_date,)
        ).fetchone()
        goal_min = goal['goal_minutes'] if goal else 120
        status = 'completed' if total >= goal_min else 'pending'
        self.conn.execute(
            "UPDATE daily_goals SET completed_minutes=?, status=? WHERE date=?",
            (total, status, target_date)
        )
        self.conn.commit()

    # ── Streak Methods ──
    def get_streak(self):
        row = self.conn.execute("SELECT * FROM streak WHERE id=1").fetchone()
        return dict(row) if row else {'current_streak': 0, 'longest_streak': 0, 'last_completed_date': None}

    def update_streak(self, current, longest, last_date):
        self.conn.execute(
            "UPDATE streak SET current_streak=?, longest_streak=?, last_completed_date=? WHERE id=1",
            (current, longest, last_date)
        )
        self.conn.commit()

    # ── Reminder Methods ──
    def log_reminder(self, target_date, delay_minutes=0):
        self.conn.execute(
            "INSERT INTO reminders (date, reminder_sent, delay_minutes) VALUES (?, 1, ?)",
            (target_date, delay_minutes)
        )
        self.conn.commit()

    # ── Settings Methods ──
    def get_setting(self, key, default=None):
        row = self.conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row['value'] if row else default

    def set_setting(self, key, value):
        self.conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, str(value))
        )
        self.conn.commit()

    def get_all_settings(self):
        rows = self.conn.execute("SELECT * FROM settings").fetchall()
        return {r['key']: r['value'] for r in rows}

    def reset_all_data(self):
        for table in ['sessions', 'daily_goals', 'reminders']:
            self.conn.execute(f"DELETE FROM {table}")
        self.conn.execute("UPDATE streak SET current_streak=0, longest_streak=0, last_completed_date=NULL WHERE id=1")
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()
