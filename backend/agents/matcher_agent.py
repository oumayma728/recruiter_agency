from .base_agent import BaseAgent
from typing import Dict, Any, List
import json

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
        # ❌ DON'T initialize scraper here - jobs are passed from main.py
        # Remove this line:
        # self.db = KeeJobScraper.KeeJobScraper()

    async def run(self, messages: list) -> dict:
        """Match candidate with available positions"""
        
        print(f"💼 {self.name}: Starting job matching...")
        
        try:
            # Parse input
            content = messages[-1].get("content", "{}")
            data = json.loads(content) if isinstance(content, str) else content
        except json.JSONDecodeError as e:
            print(f"   ❌ Error parsing input: {e}")
            return {
                "matched_jobs": [],
                "match_timestamp": "2024-03-14",
                "number_of_matches": 0
            }

        # Extract skills analysis and job list
        skills_analysis = data.get("skills_analysis", {})
        job_list = data.get("job_list", [])  # ← Jobs from main.py!
        
        if not skills_analysis:
            print("   ⚠️ No skills analysis found")
            return {
                "matched_jobs": [],
                "match_timestamp": "2024-03-14",
                "number_of_matches": 0
            }
        
        if not job_list:
            print("   ⚠️ No jobs provided")
            return {
                "matched_jobs": [],
                "match_timestamp": "2024-03-14",
                "number_of_matches": 0
            }

        # Extract candidate skills
        technical_skills = skills_analysis.get("technical_skills", [])
        tools = skills_analysis.get("tools", [])
        databases = skills_analysis.get("databases", [])
        ai_ml_skills = skills_analysis.get("ai_ml_skills", [])

        # Combine all skills
        all_skills = technical_skills + tools + databases + ai_ml_skills
        candidate_skills = list(set(all_skills))  # Remove duplicates
        
        experience_level = skills_analysis.get("experience_level", "Junior")

        print(f"   📊 Candidate has {len(candidate_skills)} skills")
        print(f"   📊 Matching against {len(job_list)} jobs")
        print(f"   📊 Experience level: {experience_level}")

        # Match candidate against jobs
        scored_jobs = self._score_jobs(candidate_skills, experience_level, job_list)

        # Sort by score and take top 3
        scored_jobs.sort(key=lambda x: int(x["match_score"].rstrip("%")), reverse=True)
        top_matches = scored_jobs[:3]

        print(f"   ✅ Found {len(scored_jobs)} matches (showing top {len(top_matches)})")

        return {
            "matched_jobs": top_matches,
            "match_timestamp": "2024-03-14",
            "number_of_matches": len(scored_jobs),
        }

    def _score_jobs(self, candidate_skills: List[str], experience_level: str, job_list: List[Dict]) -> List[Dict]:
        """
        Score jobs based on skill match and experience level
        
        Args:
            candidate_skills: List of candidate's skills
            experience_level: Candidate's experience level (Junior/Mid/Senior)
            job_list: List of available jobs
        
        Returns:
            List of scored jobs
        """
        
        scored_jobs = []
        candidate_skills_lower = set([s.lower() for s in candidate_skills])
        
        for job in job_list:
            # Calculate skill match score
            job_title = job.get('title', '').lower()
            job_description = job.get('description', '').lower()
            job_requirements = job.get('requirements', [])
            
            # Combine all job text for matching
            job_text = f"{job_title} {job_description}"
            
            # Count skill matches
            skill_matches = sum(1 for skill in candidate_skills_lower if skill in job_text)
            
            # Also check requirements if available
            if job_requirements:
                req_lower = set([r.lower() for r in job_requirements])
                req_matches = len(candidate_skills_lower.intersection(req_lower))
                skill_matches += req_matches
            
            # Calculate match score
            if skill_matches > 0:
                # Each skill match = 15%, max 100%
                match_score = min(skill_matches * 15, 100)
                
                # Only include if score >= 30%
                if match_score >= 30:
                    scored_jobs.append({
                        "title": job.get('title', 'Unknown Position'),
                        "company": job.get('company', 'Unknown Company'),
                        "match_score": f"{int(match_score)}%",
                        "location": job.get('location', 'Tunisia'),
                        "salary_range": job.get('salary_range', 'Not specified'),
                        "requirements": job.get('requirements', []),
                        "url": job.get('url', ''),
                        "source": job.get('source', 'Keejob')
                    })
        
        return scored_jobs