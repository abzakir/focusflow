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

-- Default streak row
INSERT OR IGNORE INTO streak (id, current_streak, longest_streak) VALUES (1, 0, 0);
