import sqlite3
import pandas as pd
from datetime import datetime
import os

# ---------------- Database Path ----------------
# Use Render persistent volume
DB_PATH = os.getenv("DB_PATH", "/tmp/jobs.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# ---------------- Initialize DB ----------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            location TEXT,
            job_type TEXT,
            description TEXT,
            application_link TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------- CRUD Operations ----------------
def get_all_jobs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_job(title, company, location, job_type, description, application_link):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO jobs (title, company, location, job_type, description, application_link, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, company, location, job_type, description, application_link, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def update_job(job_id, title, company, location, job_type, description, application_link):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE jobs
        SET title=?, company=?, location=?, job_type=?, description=?, application_link=?
        WHERE id=?
    """, (title, company, location, job_type, description, application_link, job_id))
    conn.commit()
    conn.close()

def delete_job(job_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE id=?", (job_id,))
    conn.commit()
    conn.close()

def clear_jobs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs")
    conn.commit()
    conn.close()

def bulk_add_jobs_from_excel(file_path):
    df = pd.read_excel(file_path)
    for _, row in df.iterrows():
        add_job(
            row.get("title",""),
            row.get("company",""),
            row.get("location",""),
            row.get("job_type",""),
            row.get("description",""),
            row.get("application_link","")
        )
