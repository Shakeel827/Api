import sqlite3
import pandas as pd
from datetime import datetime

DB_FILE = "E:\jobs.db"

def init_db():
    """
    Initialize SQLite database and create jobs table.
    Enables WAL mode for concurrency.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")  # Allow concurrent reads/writes

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            job_type TEXT,
            description TEXT,
            application_link TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def add_job(title, company, location="", job_type="", description="", application_link=""):
    """
    Add a single job to the database.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO jobs (title, company, location, job_type, description, application_link)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, company, location, job_type, description, application_link))
    conn.commit()
    conn.close()


def bulk_add_jobs_from_excel(file_path):
    """
    Import jobs from an Excel file (xlsx) into the database.
    Expected columns: title, company, location, job_type, description, application_link
    """
    df = pd.read_excel(file_path)

    # Ensure all necessary columns exist
    for col in ["title", "company", "location", "job_type", "description", "application_link"]:
        if col not in df.columns:
            df[col] = ""

    jobs = df[["title", "company", "location", "job_type", "description", "application_link"]].values.tolist()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO jobs (title, company, location, job_type, description, application_link)
        VALUES (?, ?, ?, ?, ?, ?)
    """, jobs)
    conn.commit()
    conn.close()


def get_all_jobs():
    """
    Fetch all jobs from the database, ordered by newest first.
    Returns a list of tuples.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, company, location, job_type, description, application_link, created_at
        FROM jobs
        ORDER BY created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_job(job_id, title=None, company=None, location=None, job_type=None, description=None, application_link=None):
    """
    Update a job by id. Only non-None fields will be updated.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Build dynamic query
    fields = []
    values = []
    if title is not None:
        fields.append("title = ?")
        values.append(title)
    if company is not None:
        fields.append("company = ?")
        values.append(company)
    if location is not None:
        fields.append("location = ?")
        values.append(location)
    if job_type is not None:
        fields.append("job_type = ?")
        values.append(job_type)
    if description is not None:
        fields.append("description = ?")
        values.append(description)
    if application_link is not None:
        fields.append("application_link = ?")
        values.append(application_link)

    values.append(job_id)
    sql = f"UPDATE jobs SET {', '.join(fields)} WHERE id = ?"
    cursor.execute(sql, values)
    conn.commit()
    conn.close()


def delete_job(job_id):
    """
    Delete a job by id.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()


def clear_jobs():
    """
    Delete all jobs from the database.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs")
    conn.commit()
    conn.close()


# Initialize DB automatically
init_db()
