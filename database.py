import sqlite3
import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog

DB_FILE = "jobs.db"

# ---------------- Database Functions ----------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
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
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO jobs (title, company, location, job_type, description, application_link)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, company, location, job_type, description, application_link))
    conn.commit()
    conn.close()

def bulk_add_jobs_from_excel(file_path):
    df = pd.read_excel(file_path)
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
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    fields, values = [], []
    if title is not None: fields.append("title = ?"); values.append(title)
    if company is not None: fields.append("company = ?"); values.append(company)
    if location is not None: fields.append("location = ?"); values.append(location)
    if job_type is not None: fields.append("job_type = ?"); values.append(job_type)
    if description is not None: fields.append("description = ?"); values.append(description)
    if application_link is not None: fields.append("application_link = ?"); values.append(application_link)
    values.append(job_id)
    sql = f"UPDATE jobs SET {', '.join(fields)} WHERE id = ?"
    cursor.execute(sql, values)
    conn.commit()
    conn.close()

def delete_job(job_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()

def clear_jobs():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs")
    conn.commit()
    conn.close()

# ---------------- GUI Functions ----------------
def upload_file():
    file_path = filedialog.askopenfilename(title="Select Excel file", filetypes=[("Excel files", "*.xlsx *.xls")])
    if file_path:
        try:
            bulk_add_jobs_from_excel(file_path)
            messagebox.showinfo("Success", "Jobs uploaded successfully!")
            refresh_table()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload jobs:\n{e}")

def refresh_table():
    for row in job_table.get_children():
        job_table.delete(row)
    for job in get_all_jobs():
        job_table.insert("", tk.END, values=job)

def add_job_gui():
    title = simpledialog.askstring("Input", "Job Title:")
    if not title: return
    company = simpledialog.askstring("Input", "Company:")
    if not company: return
    location = simpledialog.askstring("Input", "Location:")
    job_type = simpledialog.askstring("Input", "Job Type:")
    description = simpledialog.askstring("Input", "Description:")
    link = simpledialog.askstring("Input", "Application Link:")
    add_job(title, company, location, job_type, description, link)
    refresh_table()

def edit_selected_job():
    selected = job_table.selection()
    if not selected:
        messagebox.showwarning("Warning", "Select a job to edit!")
        return
    job_id = job_table.item(selected[0])['values'][0]
    current = job_table.item(selected[0])['values']
    title = simpledialog.askstring("Edit", "Job Title:", initialvalue=current[1])
    company = simpledialog.askstring("Edit", "Company:", initialvalue=current[2])
    location = simpledialog.askstring("Edit", "Location:", initialvalue=current[3])
    job_type = simpledialog.askstring("Edit", "Job Type:", initialvalue=current[4])
    description = simpledialog.askstring("Edit", "Description:", initialvalue=current[5])
    link = simpledialog.askstring("Edit", "Application Link:", initialvalue=current[6])
    update_job(job_id, title, company, location, job_type, description, link)
    refresh_table()

def delete_selected_jobs():
    selected = job_table.selection()
    if not selected:
        messagebox.showwarning("Warning", "Select jobs to delete!")
        return
    for item in selected:
        job_id = job_table.item(item)['values'][0]
        delete_job(job_id)
    refresh_table()

def clear_all_jobs_gui():
    if messagebox.askyesno("Confirm", "Are you sure you want to delete all jobs?"):
        clear_jobs()
        refresh_table()

# ---------------- Initialize DB ----------------
init_db()

# ---------------- Tkinter GUI ----------------
root = tk.Tk()
root.title("Job Manager")
root.geometry("1000x600")

# Buttons Frame
frame = tk.Frame(root)
frame.pack(pady=10)

tk.Button(frame, text="Upload Excel", command=upload_file, padx=15).grid(row=0, column=0, padx=5)
tk.Button(frame, text="Add Job", command=add_job_gui, padx=15).grid(row=0, column=1, padx=5)
tk.Button(frame, text="Edit Selected", command=edit_selected_job, padx=15).grid(row=0, column=2, padx=5)
tk.Button(frame, text="Delete Selected", command=delete_selected_jobs, padx=15).grid(row=0, column=3, padx=5)
tk.Button(frame, text="Clear All Jobs", command=clear_all_jobs_gui, padx=15).grid(row=0, column=4, padx=5)

# Jobs Table
columns = ("ID", "Title", "Company", "Location", "Job Type", "Description", "Link", "Created At")
job_table = ttk.Treeview(root, columns=columns, show="headings", selectmode="extended")
for col in columns:
    job_table.heading(col, text=col)
    job_table.column(col, width=120 if col=="ID" else 150, anchor="w")
job_table.pack(pady=20, fill=tk.BOTH, expand=True)

refresh_table()
root.mainloop()
