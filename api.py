# api.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import database  # your existing database.py

# FastAPI instance
app = FastAPI(title="Jobs API")

# Enable CORS for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend URL if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# API Endpoints
# ---------------------------

# Root endpoint
@app.get("/")
def root():
    return {"message": "Jobs API is running!"}

# GET all jobs
@app.get("/jobs")
def get_jobs():
    try:
        rows = database.get_all_jobs()
        jobs = [
            {
                "id": row[0],
                "title": row[1],
                "company": row[2],
                "location": row[3],
                "job_type": row[4],
                "description": row[5],
                "application_link": row[6],
                "created_at": row[7]
            }
            for row in rows
        ]
        return {"jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET single job by ID
@app.get("/jobs/{job_id}")
def get_job(job_id: int):
    try:
        job = next((j for j in database.get_all_jobs() if j[0] == job_id), None)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return {
            "id": job[0],
            "title": job[1],
            "company": job[2],
            "location": job[3],
            "job_type": job[4],
            "description": job[5],
            "application_link": job[6],
            "created_at": job[7]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET search/filter jobs
@app.get("/jobs/search")
def search_jobs(
    title: str = Query(None),
    company: str = Query(None),
    location: str = Query(None),
    job_type: str = Query(None)
):
    try:
        rows = database.get_all_jobs()
        filtered = []
        for row in rows:
            if title and title.lower() not in row[1].lower():
                continue
            if company and company.lower() not in row[2].lower():
                continue
            if location and location.lower() not in (row[3] or "").lower():
                continue
            if job_type and job_type.lower() not in (row[4] or "").lower():
                continue
            filtered.append({
                "id": row[0],
                "title": row[1],
                "company": row[2],
                "location": row[3],
                "job_type": row[4],
                "description": row[5],
                "application_link": row[6],
                "created_at": row[7]
            })
        return {"jobs": filtered}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------
# Run server
# ---------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8009, reload=True)
