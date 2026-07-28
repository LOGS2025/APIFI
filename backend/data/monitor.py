# monitor.py
import sqlite3
import json

DB_PATH = "courses.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                clave INTEGER PRIMARY KEY,
                data TEXT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

def add_course(clave, json_data):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO courses (clave, data) 
            VALUES (?, ?)
            ON CONFLICT(clave) DO UPDATE SET 
                data = excluded.data,
                last_updated = CURRENT_TIMESTAMP
            """,
            (clave, json_data)
        )

def get_course(clave):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM courses WHERE clave = ?", (clave,)).fetchone()
        if row:
            return {
                'clave': row['clave'],
                'data': json.loads(row['data']),
                'last_updated': row['last_updated']
            }
        return None

def get_all_courses():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM courses ORDER BY clave").fetchall()
        return [
            {
                'clave': row['clave'],
                'data': json.loads(row['data']),
                'last_updated': row['last_updated']
            }
            for row in rows
        ]

def delete_course(clave):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("DELETE FROM courses WHERE clave = ?", (clave,))
        return cur.rowcount > 0

# Initialize database
init_db()