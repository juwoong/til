CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    phase INTEGER NOT NULL, 
    interval TEXT NOT NULL,
    ease REAL NOT NULL,
    leech INTEGER NOT NULL,
    last_review DATETIME,   
    next_review DATETIME
);
