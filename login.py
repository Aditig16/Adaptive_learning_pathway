import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "users.db"
)

def login_user(email, password):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE email = ?
        AND password = ?
        """,
        (email, password)
    )

    user = cursor.fetchone()

    conn.close()

    return user

def register_user(
    name,
    email,
    password,
    role,
    timeline,
    experience,
    skills,
    tools_technologies
):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password,
                role,
                timeline,
                experience,
                skills,
                tools_technologies
            )
            VALUES (?,?,?,?,?,?,?,?)
            """,
            (
                name,
                email,
                password,
                role,
                timeline,
                experience,
                skills,
                tools_technologies
            )
        )

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()