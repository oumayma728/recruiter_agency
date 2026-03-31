from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
from db.database import JobDatabase
import dotenv
import json
from agents.extractor_agent import ExtractorAgent
from scrapers.Keejob_scraper import KeeJobScraper
dotenv.load_dotenv()
from agents.orchestrator_agent import OrchestratorAgent

app = FastAPI(
    title="AI Recruiter Agency API",
    description="API for processing resumes and matching them with job postings using AI.",
    version="1.0.0",
)    

origins = os.getenv("ALLOWED_ORIGINS").split(",")
# Allow CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
        db = JobDatabase()
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
        
        extractor_agent = ExtractorAgent()

        # Actually RUN the agent with proper format
        quick_extraction = await extractor_agent.run([
            {"role": "user", "content": json.dumps({"file_path": temp_file_path})}
        ])
        
        # ✅ Get the structured data from extraction results
        structured_data = quick_extraction.get("structured_data", {})
        personal_info = structured_data.get("personal_info", {})
        job_title = personal_info.get("job_title", "")
        
        # Build search keyword - SIMPLIFY IT
        search_keyword = ""
        if job_title and job_title.strip():
            # Clean the job title
            search_keyword = job_title.strip()
            
            # Remove special characters and simplify
            search_keyword = search_keyword.replace("|", " ")
            search_keyword = search_keyword.replace("&", " ")
            search_keyword = search_keyword.replace(",", " ")
            
            # Extract main keywords (first part before special chars)
            if "|" in search_keyword:
                search_keyword = search_keyword.split("|")[0].strip()
            
            # Remove "Développeuse" and use just "Développeur" or "Full Stack"
            if "développeuse" in search_keyword.lower():
                search_keyword = "Développeur Full Stack"
            
            # Or better: extract the core technologies
            tech_keywords = []
            if "React" in job_title:
                tech_keywords.append("React")
            if "Node" in job_title:
                tech_keywords.append("Node.js")
            if "Python" in job_title:
                tech_keywords.append("Python")
            if "Full-Stack" in job_title:
                tech_keywords.append("Développeur Full Stack")
            
            if tech_keywords:
                search_keyword = " ".join(tech_keywords[:2])  # Use top 2 tech keywords
            else:
                search_keyword = "Développeur Full Stack"  # Fallback
            
            print(f"🔍 Simplified keyword for search: '{search_keyword}'")
        else:
            # Default search keyword if no job title found
            search_keyword = "Développeur Full Stack"
            print(f"🔍 Using default keyword: '{search_keyword}'")
        
        scraped_jobs = []

        # Try scraping
        try:
            keejob_scraper = KeeJobScraper(headless=True)
            scraped_jobs = keejob_scraper.search_jobs(keyword=search_keyword, max_jobs=20)
            keejob_scraper.close_browser()
            
            # After scraping
            print(f"   ✅ Scraped {len(scraped_jobs)} jobs from Keejob\n")
            for i, job in enumerate(scraped_jobs[:5]):  # Show first 5
                print(f"   Job {i+1}: {job['title']} at {job['company']} - {job['location']}")
                print(f"      Skills required: {job.get('requirements', [])[:5]}")
                print(f"      Description preview: {job['description'][:100]}...\n")
        except Exception as scraping_error:
            print(f"   ⚠️ Scraping failed: {scraping_error}")
            scraped_jobs = []
        
        final_job_list = []
        if scraped_jobs and len(scraped_jobs) > 0:
            final_job_list = scraped_jobs
            print(f"✅ Using {len(scraped_jobs)} jobs from Keejob scraping\n")
        else:
            # Fallback to database
            print("⚠️ No scraped jobs found, falling back to database...\n")
            # Load jobs
            db = JobDatabase()
            all_jobs = db.get_all_jobs()
            
            # Filter to tech-related jobs if possible
            tech_keywords = ['développeur', 'developer', 'engineer', 'full stack', 'frontend', 
                           'backend', 'react', 'python', 'javascript', 'software', 'web']
            
            tech_jobs = []
            for job in all_jobs:
                title_lower = job.get('title', '').lower()
                if any(keyword in title_lower for keyword in tech_keywords):
                    tech_jobs.append(job)
            
            if tech_jobs:
                final_job_list = tech_jobs
                print(f"✅ Using {len(final_job_list)} tech jobs from database\n")
            else:
                final_job_list = all_jobs
                print(f"✅ Using {len(final_job_list)} all jobs from database\n")

        # Run AI pipeline
        orchestrator_agent = OrchestratorAgent()

        resume_data = {
            "file_path": temp_file_path
        }

        result = await orchestrator_agent.process_resume(resume_data, final_job_list)

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
        
    except Exception as e:
        print(f"❌ Error processing resume: {e}")
        raise HTTPException(status_code=500, detail=str(e))
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
            "ollama": "running"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))