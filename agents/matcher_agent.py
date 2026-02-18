from .base_agent import BaseAgent
from db.database import JobDatabase
from typing import Dict, Any, List
import json
import sqlite3

class MatchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Matcher",
            instructions=(
                "Match candidate profiles with job positions. "
                "Consider: skills match, experience level, location preferences. "
                "Provide detailed reasoning and compatibility scores. "
                "Return matches in JSON format with title, match_score, and location fields."
            ),
        )
        #Initialize the job database connection
        self.db = JobDatabase()

    async def run(self, messages: list) -> dict:
        """Match candidate with available positions"""
        try:
            #Assuming the last message contains the candidate's skills analysis in JSON format
            content = messages[-1].get("content", "{}")
            data = json.loads(content) if isinstance(content, str) else content
        except json.JSONDecodeError as e:
            print(f"Error parsing analysis results: {e}")
            return {"matched_jobs": [], "match_timestamp": "2024-03-14", "number_of_matches": 0}
        #Extract skills and experience level from the analysis results
        skills_analysis = data.get("skills_analysis", {})
        if not skills_analysis:
            print("No skills analysis found in the input data.")
            return {"matched_jobs": [], "match_timestamp": "2024-03-14", "number_of_matches": 0}
        #Combine all relevant skills into a single list and ensure it's valid
        technical_skills = skills_analysis.get("technical_skills", [])
        tools = skills_analysis.get("tools", [])
        databases = skills_analysis.get("databases", [])
        ai_ml_skills = skills_analysis.get("ai_ml_skills", [])

        skills = list(set(technical_skills + tools + databases + ai_ml_skills))
        #Extract experience level, defaulting to "Junior" if not provided or invalid
        experience_level = skills_analysis.get("experience_level", "Junior")
    
        if not isinstance(skills, list):
            skills = []
        if not skills:
            print("No valid skills found, defaulting to empty list.")

        print(f"==>>> Skills: {skills}, Experience Level: {experience_level}")
        #Search for matching jobs based on the extracted skills and experience level
        matching_jobs = self.search_jobs(skills, experience_level)

        scored_jobs = []
        candidate_skills = set(skills)

        for job in matching_jobs:
            required_skills = set(job.get("requirements", []))
            #overlap is the number of skills that match between the candidate and the job requirements, and total_required is the total number of required skills for the job. The match score is calculated as the percentage of required skills that the candidate possesses, and only jobs with a match score of 30% or higher are included in the final results. The matched jobs are then sorted by their match score in descending order, and the top 3 matches are returned along with a timestamp and the total number of matches found.
            overlap = len(required_skills.intersection(candidate_skills))

            total_required = len(required_skills)

            match_score = int((overlap / total_required) * 100) if total_required > 0 else 0

            if match_score >= 30:
                scored_jobs.append({
                    "title": f"{job['title']} at {job['company']}",
                    "match_score": f"{match_score}%",
                    "location": job.get("location"),
                    "salary_range": job.get("salary_range"),
                    "requirements": job.get("requirements", []),
                })

        scored_jobs.sort(key=lambda x: int(x["match_score"].rstrip("%")), reverse=True)

        return {
            "matched_jobs": scored_jobs[:3],
            "match_timestamp": "2024-03-14",
            "number_of_matches": len(scored_jobs),
        }

    def search_jobs(self, skills: List[str], experience_level: str) -> List[Dict[str, Any]]:
        """Search jobs by skills + experience."""

        # Map text levels to numbers (recommended)
        level_map = {"Intern": 0, "Junior": 1, "Mid": 2, "Senior": 3}
        # Get the candidate's experience level as a number, defaulting to 1 (Junior) if not found
        cand_level = level_map.get(experience_level, 1)

        # Your DB must store experience_level in a compatible way.
        # If it's stored as text, consider storing a numeric column instead.
        # Here we assume it is stored as text and we filter in Python after fetch.
        base_query = "SELECT id, title, company, location, salary_range, requirements, experience_level FROM jobs"
        
        where_clauses = []
        params = []

        for skill in skills:
            where_clauses.append("requirements LIKE ?")
            params.append(f"%{skill}%")

        query = base_query
        if where_clauses:
            query += " WHERE (" + " OR ".join(where_clauses) + ")"

        try:
            #connect to the SQLite database, execute the query with the provided parameters, and fetch all matching rows. The results are then processed to filter out jobs that exceed the candidate's experience level, and a list of matching job dictionaries is returned.
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()

            jobs = []
            for row in rows:
                job_level = level_map.get(row[6], 3)
                if job_level <= cand_level:
                    jobs.append({
                        "id": row[0],
                        "title": row[1],
                        "company": row[2],
                        "location": row[3],
                        "salary_range": row[4],
                        "requirements": json.loads(row[5]) if row[5] else [],
                        "experience_level": row[6],
                    })

            return jobs

        except Exception as e:
            print(f"Error searching for jobs: {e}")
            return []
