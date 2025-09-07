# streamlit_app.py
import streamlit as st
import pandas as pd
import database

st.set_page_config(page_title="Job Manager", layout="wide")
st.title("📋 Job Manager (Web GUI)")

# ---------------- Upload Excel ----------------
st.subheader("Upload Jobs via Excel")
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
if uploaded_file:
    try:
        database.bulk_add_jobs_from_excel(uploaded_file)
        st.success("Jobs uploaded successfully!")
    except Exception as e:
        st.error(f"Failed to upload: {e}")

# ---------------- Add Job ----------------
st.subheader("Add a New Job")
with st.form(key="add_job_form"):
    title = st.text_input("Job Title")
    company = st.text_input("Company")
    location = st.text_input("Location")
    job_type = st.text_input("Job Type")
    description = st.text_area("Description")
    link = st.text_input("Application Link")
    submitted = st.form_submit_button("Add Job")
    if submitted:
        if not title or not company:
            st.warning("Title and Company are required!")
        else:
            database.add_job(title, company, location, job_type, description, link)
            st.success("Job added successfully!")

# ---------------- Show Jobs ----------------
st.subheader("All Jobs")
jobs = database.get_all_jobs()
if jobs:
    df_jobs = pd.DataFrame(jobs, columns=["ID", "Title", "Company", "Location", "Job Type", "Description", "Link", "Created At"])
    st.dataframe(df_jobs)
else:
    st.info("No jobs found.")

# ---------------- Edit/Delete Job ----------------
st.subheader("Edit/Delete Job")
if jobs:
    job_ids = [job[0] for job in jobs]
    selected_id = st.selectbox("Select Job ID", options=job_ids)
    if selected_id:
        job = next(j for j in jobs if j[0] == selected_id)
        new_title = st.text_input("Title", job[1])
        new_company = st.text_input("Company", job[2])
        new_location = st.text_input("Location", job[3])
        new_job_type = st.text_input("Job Type", job[4])
        new_description = st.text_area("Description", job[5])
        new_link = st.text_input("Application Link", job[6])
        col1, col2 = st.columns(2)
        if col1.button("Update Job"):
            database.update_job(selected_id, new_title, new_company, new_location, new_job_type, new_description, new_link)
            st.success("Job updated successfully!")
        if col2.button("Delete Job"):
            database.delete_job(selected_id)
            st.success("Job deleted successfully!")

# ---------------- Clear All Jobs ----------------
if st.button("Clear All Jobs"):
    database.clear_jobs()
    st.warning("All jobs cleared!")
