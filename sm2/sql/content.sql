CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_id INTEGER NOT NULL,
    phase INTEGER NOT NULL, 
    interval INTEGER NOT NULL,
    ease REAL NOT NULL,
    step INTEGER NOT NULL,
    leech INTEGER NOT NULL,
    last_review TIMESTAMP,
    next_review TIMESTAMP
);

CREATE TABLE IF NOT EXISTS datas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    description TEXT NOT NULL,
    priority INTEGER NOT NULL,
    is_generated BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TIMESTAMP NOT NULL,
    status INTEGER NOT NULL, -- 0: not started, 1: in progress, 2: finished
    created TEXT NOT NULL DEFAULT '[]',
    learning TEXT NOT NULL DEFAULT '[]',
    reviewed TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT
);