print("IMPORT SCRIPT STARTED")
import sqlite3
import pandas as pd

df = pd.read_excel(
    "data/HCAI_User_dataset.xlsx"
)
print(df.head())
print("Rows:", len(df))

conn = sqlite3.connect(
    "database/users.db"
)

cursor = conn.cursor()

for _, row in df.iterrows():

    name = str(row["Full Name"]).strip()

    email = (
        name.lower()
        .replace(" ", ".")
        + "@gmail.com"
    )

    password = "1234"

    role = row["What IT role are you targeting?"]

    timeline = row["What is your target timeline?"]

    experience = row["Overall IT Experience"]

    skills = ""

    tools_technologies = ""

    if pd.notna(row["Skills you already know?"]):

        skills = str(
            row["Skills you already know?"]
        ).strip()

    if pd.notna(row["Tools & Technologies you already know?"]):

        tools_technologies = str(
            row["Tools & Technologies you already know?"]
        ).strip()

      
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

    except Exception as e:
        print("ERROR:", e)
    
    cursor.execute("SELECT COUNT(*) FROM users")
    print("Before Commit:", cursor.fetchone()[0])

conn.commit()

cursor.execute("SELECT COUNT(*) FROM users")
print("After Commit:", cursor.fetchone()[0])

conn.close()

print("Users Imported Successfully")