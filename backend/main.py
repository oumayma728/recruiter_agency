from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import dotenv
import json
from agents.ResumeAnalyzerAgent import ResumeAnalyzerAgent
from scrapers.jobspy_scraper import JobSpyScraper
from scrapers.Keejob_scraper import KeeJobScraper
dotenv.load_dotenv()
from agents.orchestrator_agent import OrchestratorAgent

app = FastAPI(
    title="AI Recruiter Agency API",
    description="API for processing resumes and matching them with job postings using AI.",
    version="1.0.0",
)    

origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
# Allow CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
)
# Directory to save uploaded resumes
UPLOAD_DIR = "uploads"
# Ensure the upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)
def _build_search_keyword(job_title: str, technical_skills: list) -> str:
    """Build search keyword from job title and skills."""
    
    default_keyword = "Développeur Full Stack"
    
    if not job_title and not technical_skills:
        return default_keyword
    
    # Priority 1: Use job title if available and meaningful
    if job_title and len(job_title) > 3:
        # Clean the job title
        clean_title = job_title.strip()
        
        # Remove common filler words
        stop_words = ["développeuse", "junior", "senior", "lead", "principal"]
        for word in stop_words:
            clean_title = clean_title.replace(word, "").strip()
        
        # Extract main role
        if "full" in clean_title.lower() and "stack" in clean_title.lower():
            return "Développeur Full Stack"
        elif "frontend" in clean_title.lower() or "front" in clean_title.lower():
            return "Développeur Frontend"
        elif "backend" in clean_title.lower() or "back" in clean_title.lower():
            return "Développeur Backend"
        elif "data" in clean_title.lower():
            return "Data Engineer"
        elif "devops" in clean_title.lower():
            return "DevOps Engineer"
        
        return clean_title
    
    # Priority 2: Use top technical skill
    if technical_skills:
        top_skills = ["Python", "JavaScript", "React", "Node.js", "Java", "AWS"]
        for skill in top_skills:
            if skill.lower() in [s.lower() for s in technical_skills]:
                return f"Développeur {skill}"
    
    return default_keyword

def _is_tech_job(job: dict) -> bool:
    """Check if a job is tech-related."""
    title = (job.get("title") or "").lower()
    description = (job.get("description") or "").lower()
    requirements = " ".join(job.get("requirements") or []).lower()
    
    haystack = f"{title} {description} {requirements}"
    
    tech_tokens = [
        "developpeur", "développeur", "developer", "software", "engineer",
        "full stack", "frontend", "backend", "web", "react", "node",
        "python", "javascript", "typescript", "api", "devops", "data",
        "informatique", "programming", "coding"
    ]
    
    return any(token in haystack for token in tech_tokens)


def _country_matches_job(job: dict, country: str) -> bool:
    """Check whether a job location matches selected country."""
    selected = (country or "").strip().lower()
    if not selected or selected == "remote":
        return True

    location_text = (job.get("location") or "").lower()
    title_text = (job.get("title") or "").lower()
    description_text = (job.get("description") or "").lower()
    haystack = f"{location_text} {title_text} {description_text}"

    aliases = {
        "usa": ["usa", "united states", "u.s.", "us"],
        "uk": ["uk", "united kingdom", "england", "london", "britain", "great britain"],
        "germany": ["germany", "deutschland", "berlin", "munich", "hamburg", "frankfurt"],
        "france": ["france", "paris", "lyon", "marseille", "toulouse"],
        "tunisia": ["tunisia", "tunisie", "tunis", "sfax", "sousse"],
        "canada": ["canada", "toronto", "montreal", "vancouver", "ottawa"],
        "india": ["india", "bangalore", "bengaluru", "mumbai", "delhi", "hyderabad", "pune"],
    }

    tokens = aliases.get(selected, [selected])
    return any(token in haystack for token in tokens)

async def _scrape_jobs(keyword: str, location: str, country: str = "usa", scraper_source: str = "platforms") -> list:
    """Scrape jobs from multiple sources."""
    scraped_jobs = []

    source = (scraper_source or "platforms").strip().lower()

    if source == "keejob":
        try:
            print("🌍 Scraping jobs from Keejob...")
            keejob_scraper = KeeJobScraper(headless=True)
            scraped_jobs = keejob_scraper.search_jobs(keyword=keyword, max_jobs=20)
            keejob_scraper.close_browser()
            print(f"   ✅ Scraped {len(scraped_jobs)} jobs from Keejob")
        except Exception as e:
            print(f"   ⚠️ Keejob failed: {e}")
    else:
        try:
            print(f"🌍 Scraping jobs from JobSpy platforms for {country}...")
            jobspy_scraper = JobSpyScraper()
            scraped_jobs = jobspy_scraper.search_jobs(
                keyword=keyword,
                location=location,
                max_jobs=20,
                country=country,
            )
            print(f"   ✅ Scraped {len(scraped_jobs)} jobs from JobSpy")
        except Exception as e:
            print(f"   ⚠️ JobSpy failed: {e}")

    # Filter to tech jobs only
    scraped_jobs = [job for job in scraped_jobs if _is_tech_job(job)]

    # Keep only jobs matching the selected country (except remote searches).
    scraped_jobs = [job for job in scraped_jobs if _country_matches_job(job, country)]

    return scraped_jobs
@app.get("/")
def root():
    return {"message": "AI Recruiter API running"}


@app.post("/api/analyze_resume")
async def analyze_resume(
    file: UploadFile = File(...),
    country: str = Form("usa"),
    scraper_source: str = Form("platforms"),
):
    """Process resume with optimized 3-agent pipeline."""
    
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
        
        # ========== STEP 1: Analyze Resume (Extraction + Analysis) ==========
        print("📝 Analyzing resume with ResumeAnalyzerAgent...")
        resume_analyzer = ResumeAnalyzerAgent()
        analysis_result = await resume_analyzer.run([
            {"role": "user", "content": json.dumps({"file_path": temp_file_path})}
        ])
        
        if analysis_result.get("status") != "completed":
            raise HTTPException(
                status_code=500,
                detail=f"Resume analysis failed: {analysis_result.get('error', 'Unknown error')}"
            )
        
        # Extract candidate info for job search
        structured_data = analysis_result.get("structured_data", {})
        candidate_analysis = analysis_result.get("analysis", {})
        personal_info = structured_data.get("personal_info", {})
        
        # Get job title (now from analysis, not manual extraction)
        job_title = personal_info.get("job_title", "")
        job_location = personal_info.get("location", "")
        
        # Get skills for better search keywords
        skills = structured_data.get("skills", {})
        technical_skills = skills.get("technical", [])
        
        print(f"   ✅ Candidate: {personal_info.get('name', 'Unknown')}")
        print(f"   ✅ Experience: {candidate_analysis.get('years_of_experience', 0)} years")
        print(f"   ✅ Skills: {len(technical_skills)} technical skills")
        
        # ========== STEP 2: Build Search Keywords from Resume ==========
        search_keyword = _build_search_keyword(job_title, technical_skills)
        print(f"🔍 Search keyword: '{search_keyword}'")
        
        # ========== STEP 3: Scrape Jobs ==========
        print(f"🧭 Scraper source selected: {scraper_source}")
        scraped_jobs = await _scrape_jobs(search_keyword, job_location, country, scraper_source)
        final_job_list = scraped_jobs
        print(f"✅ Using {len(scraped_jobs)} scraped jobs")
        
        # ========== STEP 4: Run Orchestrator with New Agents ==========
        print("\n🚀 Running orchestrator with optimized agents...")
        orchestrator = OrchestratorAgent()
        
        result = await orchestrator.process_resume(
            resume_input={"file_path": temp_file_path},
            job_list=final_job_list
        )
        
        if result.get("workflow_status") == "failed":
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Unknown error during resume processing")
            )
        
        # ========== STEP 5: Return Response ==========
        # Transform orchestrator result into frontend-expected structure
        skills_data = structured_data.get("skills", {})
        ranking_results = result.get("ranking_results", {})
        recommendation = result.get("recommendation", {})
        enhancement_results = result.get("enhancement_results", {})
        
        return {
            "success": True,
            "message": "Resume processed successfully",
            "data": {
                # Skills Analysis Section (for SkillsAnalysis component)
                "analysis_results": {
                    "skills_analysis": {
                        "technical_skills": skills_data.get("technical", []),
                        "tools": skills_data.get("tools", []),
                        "databases": skills_data.get("databases", []),
                        "job_title": personal_info.get("job_title", ""),
                        "years_of_experience": candidate_analysis.get("years_of_experience", 0),
                        "experience_level": candidate_analysis.get("experience_level", "Unknown")
                    }
                },
                
                # Job Matches Section (for JobMatches component)
                "match_results": {
                    "matched_jobs": ranking_results.get("top_recommendations", [])
                },
                
                # Recommendations Section (for Recommendations component)
                "recommendation_results": {
                    "hiring_recommendation": recommendation.get("hiring_recommendation", "PASS"),
                    "overall_assessment": recommendation.get("overall_assessment", ""),
                    "confidence_level": recommendation.get("confidence_level", "LOW"),
                    "strengths": recommendation.get("strengths", []),
                    "concerns": recommendation.get("concerns", []),
                    "next_steps": recommendation.get("next_steps", []),
                    "interview_questions": recommendation.get("interview_questions", [])
                },
                
                # Enhancement Results
                "enhancement_results": {
                    "recommendations": enhancement_results.get("recommendations", []),
                    "skipped": enhancement_results.get("skipped", False)
                },
                
                # Candidate Info
                "candidate": {
                    "name": personal_info.get("name", "Unknown"),
                    "email": personal_info.get("email", ""),
                    "job_title": personal_info.get("job_title", ""),
                    "experience_years": candidate_analysis.get("years_of_experience", 0),
                    "experience_level": candidate_analysis.get("experience_level", "Unknown"),
                    "top_skills": technical_skills[:5]
                },
                
                # Summary stats
                "workflow_summary": {
                    "status": result.get("workflow_status"),
                    "stages_completed": result.get("current_stage"),
                    "scraper_source": scraper_source,
                    "jobs_analyzed": len(final_job_list),
                    "jobs_passed_screening": ranking_results.get("screening_summary", {}).get("passed_screening", 0)
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error processing resume: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                print(f"Error deleting temp file: {e}")

