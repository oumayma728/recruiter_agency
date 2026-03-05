from fastapi import FastAPI , UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
from db.database import JobDatabase
from agents.orchestrator_agent import OrchestratorAgent
app = FastAPI(
    title="AI Recruiter Agency API",
    description="API for processing resumes and matching them with job postings using AI.",
    version="1.0.0",
)
# Allow CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000"
    ],
)
# Directory to save uploaded resumes
UPLOAD_DIR = "uploads"
# Ensure the upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def root():
    return {"message": "AI Recruiter API running"}


@app.get("/api/jobs")
def get_jobs():
    """Get all available job postings."""
    try:
        db= JobDatabase()
        jobs = db.get_all_jobs()
        return {
            "success": True,
            "jobs": jobs,
            "count": len(jobs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/{job_id}")
def get_job(job_id: int):
    """Get details of a specific job posting by ID."""
    try:
        db = JobDatabase()
        job = db.get_job_by_id(job_id)
        if job:
            return {
                "success": True,
                "job": job
            }
        else:
            raise HTTPException(status_code=404, detail="Job not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze_resume")
async def analyze_resume(file: UploadFile = File(...)):

    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    temp_file_path = None

    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
            dir=UPLOAD_DIR
        ) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            temp_file_path = tmp_file.name

        # Load jobs
        db = JobDatabase()
        job_list = db.get_all_jobs()

        # Run AI pipeline
        orchestrator_agent = OrchestratorAgent()

        resume_data = {
            "file_path": temp_file_path
        }

        result = await orchestrator_agent.process_resume(resume_data, job_list)

        if result.get("workflow_status") == "failed":
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Unknown error during resume processing")
            )

        return {
            "success": True,
            "message": "Resume processed successfully",
            "data": result
        }

    finally:
        # Delete temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                print(f"Error deleting temporary file: {e}")


@app.get("/api/health")
def health_check():
    """Detailed health check"""
    try:
        db = JobDatabase()
        job_count = len(db.get_all_jobs())
        return {
            "status": "healthy",
            "database": {
                "job_count": job_count
            },
            "ollama":"running"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))