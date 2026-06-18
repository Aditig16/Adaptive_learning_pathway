import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "users.db"
)

os.makedirs(
    os.path.dirname(DB_PATH),
    exist_ok=True
)

conn = sqlite3.connect(DB_PATH)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT,

    email TEXT UNIQUE,

    password TEXT,

    role TEXT,

    timeline TEXT,

    experience TEXT,

    skills TEXT,

    tools_technologies TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS assessment_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    skill_scores TEXT
)
""")

conn.commit()

conn.close()

print("DB PATH =", DB_PATH)
print("Database Created Successfully")