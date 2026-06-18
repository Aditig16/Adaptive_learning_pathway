import sqlite3
import os
import json

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

def save_assessment_result(
    user_id,
    report
):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO assessment_results
        (
            user_id,
            skill_scores
        )
        VALUES (?,?)
        """,
        (
            user_id,
            json.dumps(report)
        )
    )

    conn.commit()

    conn.close()

def get_assessment_history(
    user_id
):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            assessment_date,
            skill_scores
        FROM assessment_results
        WHERE user_id = ?
        ORDER BY assessment_date DESC
        """,
        (user_id,)
    )

    results = cursor.fetchall()

    conn.close()

    return results