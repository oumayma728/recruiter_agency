import json
from typing import Dict, Any, List
from .base_agent import BaseAgent

class RankingAgent(BaseAgent):
    """
    Merged Matcher + Screener + Recommender.
    Scores, filters, AND recommends in ONE pass.
    """
    
    def __init__(self):
        super().__init__(
            name="RankingAgent",
            instructions=(
                "Score candidates against jobs, screen based on fit, "
                "and provide final recommendations in ONE pass."
            ),
        )
    
    async def run(self, messages: list) -> Dict[str, Any]:
        """
        Input: {
            "candidate_profile": {...},  # from ResumeAnalyzer
            "job_list": [...]             # from scraper
        }
        
        Output: {
            "ranked_jobs": [...],         # scored and filtered
            "top_recommendations": [...], # top 3 with reasoning
            "screening_summary": {...}    # pass/fail stats
        }
        """
        print(f"🎯 {self.name}: Starting unified ranking & screening...")
        
        try:
            # Parse input
            content = messages[-1]["content"]
            data = json.loads(content) if isinstance(content, str) else content
            
            candidate_profile = data.get("candidate_profile", {})
            job_list = data.get("job_list", [])
            
            if not candidate_profile:
                return {"error": "No candidate profile provided", "status": "failed"}
            
            if not job_list:
                return {"error": "No jobs to match", "status": "failed"}
            
            # Extract candidate data (from ResumeAnalyzer output)
            skills = candidate_profile.get("skills", {})
            analysis = candidate_profile.get("analysis", {})
            
            candidate_skills = skills.get("technical", []) + skills.get("tools", []) + skills.get("databases", [])
            candidate_skills = list(set(candidate_skills))  # Dedupe
            
            years_exp = analysis.get("years_of_experience", 0)
            level = analysis.get("experience_level", "Junior")
            achievements = analysis.get("key_achievements", [])
            domain = analysis.get("domain_expertise", [])
            
            print(f"   📊 Candidate: {len(candidate_skills)} skills, {years_exp} years ({level})")
            print(f"   📊 Matching against {len(job_list)} jobs")
            
            # STEP 1: Score all jobs (rule-based, no LLM - FAST)
            scored_jobs = self._score_jobs(candidate_skills, years_exp, level, job_list)
            
            # STEP 2: Filter low scores (no LLM)
            qualified_jobs = [j for j in scored_jobs if j["score"] >= 40]
            print(f"   ✅ {len(qualified_jobs)}/{len(job_list)} jobs passed initial screening")
            
            if not qualified_jobs:
                return self._no_matches_response(candidate_profile)
            
            # STEP 3: ONE LLM call for detailed analysis of top jobs
            top_jobs = qualified_jobs[:5]  # Only analyze top 5 with LLM
            detailed_analysis = await self._analyze_top_jobs(
                candidate_profile, 
                top_jobs,
                candidate_skills,
                years_exp
            )
            
            # STEP 4: Combine results
            final_recommendations = self._merge_results(top_jobs, detailed_analysis)
            
            print(f"   🎯 Final recommendations: {len(final_recommendations)} jobs")
            
            return {
                "ranked_jobs": scored_jobs,  # All jobs with scores
                "top_recommendations": final_recommendations,  # Top 3 with reasoning
                "screening_summary": {
                    "total_jobs": len(job_list),
                    "passed_screening": len(qualified_jobs),
                    "analyzed_in_depth": len(top_jobs),
                    "final_recommendations": len(final_recommendations)
                },
                "candidate_summary": {
                    "experience_years": years_exp,
                    "level": level,
                    "primary_skills": candidate_skills[:5],
                    "domain_expertise": domain[:3]
                },
                "status": "completed"
            }
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e), "status": "failed"}
    
    def _score_jobs(self, candidate_skills: List[str], years_exp: float, 
                    level: str, job_list: List[Dict]) -> List[Dict]:
        """
        Rule-based scoring (FAST - no LLM)
        Returns jobs with scores 0-100
        """
        candidate_skills_lower = set(s.lower() for s in candidate_skills)
        scored_jobs = []
        
        for job in job_list:
            # Get job requirements
            job_requirements = job.get("requirements", [])
            job_title = job.get("title", "").lower()
            job_description = job.get("description", "").lower()
            
            # Enhance requirements from title if missing
            if not job_requirements:
                job_requirements = self._infer_skills_from_title(job_title)
            
            job_skills_lower = set(s.lower() for s in job_requirements)
            
            # Skill match score
            common_skills = candidate_skills_lower.intersection(job_skills_lower)
            skill_match_pct = min((len(common_skills) / max(len(job_skills_lower), 1)) * 100, 100)
            
            # Experience match score
            exp_score = self._score_experience_match(level, job_title, job_description)
            
            # Location match (if applicable)
            location_score = 20 if self._location_matches(job, candidate_profile={}) else 0
            
            # Final weighted score
            final_score = (skill_match_pct * 0.6) + (exp_score * 0.3) + (location_score * 0.1)
            final_score = min(max(final_score, 0), 100)
            
            scored_jobs.append({
                "title": job.get("title", "Unknown"),
                "company": job.get("company", "Unknown"),
                "location": job.get("location", "Tunisia"),
                "score": round(final_score),
                "skill_match_pct": round(skill_match_pct),
                "matched_skills": list(common_skills)[:5],
                "requirements": job_requirements,
                "url": job.get("url", ""),
                "source": job.get("source", "Keejob")
            })
        
        # Sort by score descending
        scored_jobs.sort(key=lambda x: x["score"], reverse=True)
        return scored_jobs
    
    def _infer_skills_from_title(self, title: str) -> List[str]:
        """Infer required skills from job title (rule-based)"""
        title_lower = title.lower()
        
        skill_maps = {
            "full-stack": ["javascript", "react", "node.js", "python", "sql", "git"],
            "frontend": ["javascript", "react", "vue", "angular", "html", "css"],
            "backend": ["python", "java", "node.js", "sql", "rest api"],
            "data": ["python", "sql", "pandas", "machine learning"],
            "devops": ["docker", "kubernetes", "aws", "linux", "ci/cd"],
            "mobile": ["react native", "flutter", "swift", "kotlin"],
            "ai": ["python", "tensorflow", "pytorch", "langchain"],
        }
        
        for key, skills in skill_maps.items():
            if key in title_lower:
                return skills
        
        return ["javascript", "python", "sql", "git"]  # Default
    
    def _score_experience_match(self, candidate_level: str, job_title: str, job_desc: str) -> float:
        """Score experience level match (0-100)"""
        text = (job_title + " " + job_desc).lower()
        
        if candidate_level == "Junior":
            if any(word in text for word in ["junior", "entry", "trainee", "stagiaire", "0-2"]):
                return 100
            elif "senior" in text or "lead" in text or "5+" in text:
                return 20
            else:
                return 60  # Neutral for mid-level jobs
                
        elif candidate_level == "Mid":
            if any(word in text for word in ["mid", "mid-level", "2-5"]):
                return 100
            elif "junior" in text or "entry" in text:
                return 40
            elif "senior" in text or "lead" in text:
                return 50
            else:
                return 70
                
        else:  # Senior
            if any(word in text for word in ["senior", "lead", "principal", "5+"]):
                return 100
            elif "junior" in text or "entry" in text:
                return 10
            else:
                return 60
        
        return 50
    
    def _location_matches(self, job: Dict, candidate_profile: Dict) -> bool:
        """Check location match (simplified)"""
        # Could be expanded with actual candidate location
        return True  # Default to true for now
    
    async def _analyze_top_jobs(self, candidate_profile: Dict, top_jobs: List[Dict],
                                 candidate_skills: List[str], years_exp: float) -> List[Dict]:
        """
        ONE LLM call to analyze top jobs with detailed reasoning
        Replaces Screener + Recommender LLM calls
        """
        if not top_jobs:
            return []
        
        print(f"   🤖 Analyzing top {len(top_jobs)} jobs with LLM...")
        
        # Prepare job summaries
        jobs_summary = []
        for i, job in enumerate(top_jobs[:3]):  # Only top 3 for detailed analysis
            jobs_summary.append({
                "rank": i + 1,
                "title": job["title"],
                "company": job["company"],
                "score": job["score"],
                "matched_skills": job["matched_skills"][:5]
            })
        
        prompt = f"""
Analyze this candidate against their top job matches and return ONLY valid JSON.

CANDIDATE:
- Years Experience: {years_exp}
- Top Skills: {', '.join(candidate_skills[:10])}

TOP JOBS:
{json.dumps(jobs_summary, indent=2)}

For EACH job, provide:
1. Hiring recommendation (PROCEED / CONSIDER / PASS)
2. Strengths (2-3 items)
3. Concerns (1-2 items)
4. Interview questions specific to this role

Return ONLY this JSON format:
{{
    "job_analyses": [
        {{
            "title": "Job Title",
            "hiring_recommendation": "PROCEED",
            "strengths": ["strength1", "strength2"],
            "concerns": ["concern1"],
            "interview_questions": ["q1", "q2"],
            "reasoning": "Brief explanation"
        }}
    ],
    "overall_recommendation": {{
        "best_fit_job": "Best job title",
        "confidence": "high/medium/low",
        "next_steps": ["step1", "step2"]
    }}
}}
"""
        
        response = self._query_ollama(prompt)
        result = self._parse_json_safely(response)
        
        if "error" in result:
            print(f"   ⚠️ LLM analysis failed: {result['error']}")
            return self._fallback_analysis(top_jobs)
        
        return result.get("job_analyses", [])
    
    def _merge_results(self, top_jobs: List[Dict], detailed_analysis: List[Dict]) -> List[Dict]:
        """Merge scoring with LLM analysis"""
        final = []
        
        # Create lookup for analysis by title
        analysis_map = {a.get("title", "").lower(): a for a in detailed_analysis}
        
        for job in top_jobs[:3]:  # Return top 3
            title_lower = job["title"].lower()
            analysis = analysis_map.get(title_lower, {})
            
            final.append({
                "title": job["title"],
                "company": job["company"],
                "match_score": f"{job['score']}%",
                "location": job["location"],
                "matched_skills": job["matched_skills"],
                "hiring_recommendation": analysis.get("hiring_recommendation", "CONSIDER"),
                "strengths": analysis.get("strengths", []),
                "concerns": analysis.get("concerns", []),
                "interview_questions": analysis.get("interview_questions", []),
                "reasoning": analysis.get("reasoning", ""),
                "url": job.get("url", "")
            })
        
        return final
    
    def _fallback_analysis(self, top_jobs: List[Dict]) -> List[Dict]:
        """Fallback when LLM fails"""
        return [{
            "title": job["title"],
            "hiring_recommendation": "CONSIDER",
            "strengths": ["Skills match detected", "Experience level appropriate"],
            "concerns": ["Manual review recommended"],
            "interview_questions": [
                "Tell me about your experience with relevant technologies",
                "Describe a challenging project you've worked on"
            ],
            "reasoning": f"{job['skill_match_pct']}% skill match"
        } for job in top_jobs[:3]]
    
    def _no_matches_response(self, candidate_profile: Dict) -> Dict:
        """Return when no jobs match"""
        return {
            "ranked_jobs": [],
            "top_recommendations": [],
            "screening_summary": {
                "total_jobs": 0,
                "passed_screening": 0,
                "analyzed_in_depth": 0,
                "final_recommendations": 0
            },
            "candidate_summary": {
                "experience_years": candidate_profile.get("analysis", {}).get("years_of_experience", 0),
                "level": candidate_profile.get("analysis", {}).get("experience_level", "Unknown"),
                "primary_skills": []
            },
            "message": "No matching jobs found. Try broadening search criteria.",
            "status": "no_matches"
        }