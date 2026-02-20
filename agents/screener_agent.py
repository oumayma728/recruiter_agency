import json
from typing import List, Dict, Any
from .base_agent import BaseAgent

class ScreenerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Screener",
            instructions=(
                """You are an expert HR screener. Screen candidates based on:
                - Qualification alignment
                - Experience relevance
                - Skill match percentage
                - Red flags or concerns
                Return ONLY valid JSON, no explanations."""
            ),
        )

    async def run(self, messages: List) -> Dict[str, Any]:
        print(f"🔍 {self.name}: Starting screening process...")
        try:
            last_message = messages[-1]["content"]
            data = json.loads(last_message) if isinstance(last_message, str) else last_message

            skills_analysis = data.get("skills_analysis") or {}
            matched_jobs = data.get("matched_jobs") or []

            if not matched_jobs:
                return {
                    "screened_jobs": [],
                    "screening_status": "failed",
                    "error": "No matched jobs to screen"
                }

            screening_results = []

            for job in matched_jobs:
                prompt = f"""
                Candidate Profile:
                - Experience: {skills_analysis.get('years_of_experience', 0)} years
                - Level: {skills_analysis.get('experience_level', 'Unknown')}
                - Technical Skills: {skills_analysis.get('technical_skills', [])}
                - Tools: {skills_analysis.get('tools', [])}
                - Databases: {skills_analysis.get('databases', [])}
                - Domain Expertise: {skills_analysis.get('domain_expertise', [])}

                Job:
                - Title: {job.get('title')}
                - Location: {job.get('location')}
                - Salary: {job.get('salary_range')}
                - Requirements: {job.get('requirements')}
                - Match Score: {job.get('match_score')}

                Return ONLY this JSON:
                {{
                    "title": "{job.get('title')}",
                    "decision": "pass or fail",
                    "screening_score": 0,
                    "reason": "short explanation",
                    "strengths": [],
                    "weaknesses": [],
                    "red_flags": []
                }}
                """
                response = self._query_ollama(prompt)
                response_data = self._parse_json_safely(response)

                if "error" not in response_data:
                    screening_results.append(response_data)
                else:
                    print(f"   ⚠️ Screening failed for {job.get('title')}: {response_data['error']}")

            # ✅ outside the loop
            total_passed = len([j for j in screening_results if j.get("decision") == "pass"])
            print(f"   ✅ Screening complete: {total_passed}/{len(matched_jobs)} jobs passed")

            # ✅ return is now here
            return {
                "screened_jobs": screening_results,
                "screening_status": "completed",
                "total_passed": total_passed
            }

        except Exception as e:
            print(f"Screener error: {str(e)}")
            return {
                "screened_jobs": [],
                "screening_status": "failed",
                "error": str(e)
            }