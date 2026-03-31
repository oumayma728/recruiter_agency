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
        top_matches = scored_jobs[:5]

        print(f"   ✅ Found {len(scored_jobs)} matches (showing top {len(top_matches)})")

        return {
            "matched_jobs": top_matches,
            "match_timestamp": "2024-03-14",
            "number_of_matches": len(scored_jobs),
        }

    def _score_jobs(self, candidate_skills: List[str], experience_level: str, job_list: List[Dict]) -> List[Dict]:
        """
        Score jobs based on skill match and experience level
        """
        
        scored_jobs = []
        candidate_skills_lower = set([s.lower() for s in candidate_skills])
        
        # Common skill mappings for job titles
        title_skill_mappings = {
            # General full-stack (detect from description)
            'full-stack': {
                'keywords': ['react', 'angular', 'vue', 'node.js', 'python', 'java', 'php', 'c#', 'javascript'],
                'common': ['javascript', 'html', 'css', 'git', 'rest api']
            },
            
            # Specific stacks
            'mern': ['mongodb', 'express', 'react', 'node.js', 'javascript'],
            'mean': ['mongodb', 'express', 'angular', 'node.js', 'javascript'],
            'lamp': ['linux', 'apache', 'mysql', 'php'],
            'django': ['python', 'django', 'postgresql', 'html', 'css'],
            'spring': ['java', 'spring', 'spring boot', 'mysql', 'maven'],
            'laravel': ['php', 'laravel', 'mysql', 'javascript'],
            'asp.net': ['c#', 'asp.net', 'mssql', 'javascript', 'html'],
            'ai': ['python', 'tensorflow', 'pytorch', 'machine learning', 'openai'],
            
            # Frontend specific
            'frontend': ['react', 'angular', 'vue', 'javascript', 'html', 'css', 'typescript'],
            
            # Backend specific  
            'backend': ['python', 'java', 'node.js', 'c#', 'sql', 'rest api', 'microservices'],
            
            # Mobile specific
            'mobile': ['react native', 'flutter', 'swift', 'kotlin', 'android', 'ios']
        }
        
        for job in job_list:
            job_title = job.get('title', '').lower()
            job_description = job.get('description', '').lower()
            
            # Get existing requirements or create from title
            job_requirements = job.get('requirements', [])
            
            # If requirements are empty or only generic, add skills based on title
            if not job_requirements or len(job_requirements) <= 1:
                # Check title against mappings
                enhanced_skills = []
                for key, skills in title_skill_mappings.items():
                    if key in job_title:
                        enhanced_skills.extend(skills)
                
                if enhanced_skills:
                    job_requirements = list(set(enhanced_skills))  # Remove duplicates
                    print(f"   🔧 Enhanced skills for '{job.get('title')}': {job_requirements[:5]}...")
            
            # Convert to lowercase for matching
            job_skills_lower = set([s.lower() for s in job_requirements])
            
            # Find common skills
            common_skills = candidate_skills_lower.intersection(job_skills_lower)
            skill_matches = len(common_skills)
            
            # Calculate skill score (max 100%)
            max_skills = 10
            skill_score = min((skill_matches / max_skills) * 100, 100)
            
            # Experience level matching
            exp_score = 0
            if experience_level == "Junior":
                if 'junior' in job_title or 'débutant' in job_description or 'stagiaire' in job_description:
                    exp_score = 20
                else:
                    exp_score = 10  # Neutral for jobs that don't specify
            elif experience_level == "Mid":
                if not ('junior' in job_title or 'senior' in job_title):
                    exp_score = 20
                else:
                    exp_score = 5
            else:  # Senior
                if 'senior' in job_title or 'lead' in job_title:
                    exp_score = 20
                else:
                    exp_score = 5
            
            # Final score (skill 80% + experience 20%)
            final_score = (skill_score * 0.8) + exp_score
            
            # Debug output
            print(f"   Job: {job.get('title', 'Unknown')[:40]}")
            print(f"      Candidate skills: {list(candidate_skills_lower)[:5]}")
            print(f"      Job skills: {list(job_skills_lower)[:5]}")
            print(f"      Common skills: {list(common_skills)[:5]}")
            print(f"      Skill matches: {skill_matches}/{max_skills}")
            print(f"      Skill score: {skill_score:.0f}%")
            print(f"      Experience score: {exp_score}")
            print(f"      Final score: {final_score:.0f}%")
            
            # Only include if score >= 30%
            if final_score >= 30:
                scored_jobs.append({
                    "title": job.get('title', 'Unknown Position'),
                    "company": job.get('company', 'Unknown Company'),
                    "match_score": f"{int(final_score)}%",
                    "location": job.get('location', 'Tunisia'),
                    "salary_range": job.get('salary_range', 'Not specified'),
                    "requirements": job_requirements,
                    "matched_skills": list(common_skills)[:5],
                    "url": job.get('url', ''),
                    "source": job.get('source', 'Keejob')
                })
        
        # Sort by score
        scored_jobs.sort(key=lambda x: int(x["match_score"].rstrip("%")), reverse=True)
        
        if not scored_jobs:
            print(f"   ⚠️ No matches found. Check candidate skills and job requirements.")
            print(f"   Candidate skills sample: {list(candidate_skills_lower)[:10]}")
        
        return scored_jobs