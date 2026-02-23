import json
from typing import Dict, Any
from .base_agent import BaseAgent
class RecommenderAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Recommender",
            instructions=(
            """Generate final recommendations considering:
            1. Extracted profile
            2. Skills analysis
            3. Job matches
            4. Screening results
            Provide clear next steps and specific recommendations.""",
        )
            )
    async def run(self,messages:list) ->Dict[str,Any]:
        print(f"💡 {self.name}: Generating final recommendations...")
        try:
            last_message = messages[-1]["content"]
            data = json.loads(last_message) if isinstance(last_message, str) else last_message

            # Extract data from previous agents
            extraction = last_message.get("extraction_results", {})
            analysis = last_message.get("analysis_results", {})
            matches = last_message.get("match_results", {})

            skills_analysis = analysis.get("skills_analysis", {})
            matched_jobs = matches.get("matched_jobs", [])
            recommendation_prompt = f"""
                Analyze this candidate and return ONLY valid JSON.

                CANDIDATE:
                Technical Skills: {skills_analysis.get('technical_skills', [])[:10]}
                Experience: {skills_analysis.get('years_of_experience', 0)} years
                Level: {skills_analysis.get('experience_level', 'Unknown')}

                TOP JOBS:
                {json.dumps(matched_jobs[:2], indent=2)}

                Return ONLY this JSON structure (no markdown, no explanation):
                {{
                "overall_assessment": "brief summary",
                "hiring_recommendation": "PROCEED/CONSIDER/PASS",
                "confidence_level": "high/medium/low",
                "strengths": ["strength1", "strength2"],
                "concerns": ["concern1"],
                "next_steps": ["step1", "step2"],
                "interview_questions": ["q1", "q2"]
                }}
            """.strip()
            print (f"   🧠 Generating recommendation with prompt:\n{recommendation_prompt}\n")
            response = self._query_ollama(recommendation_prompt)
            response_data = self._parse_json_safely(response)
            if "error" in response_data:
                print(f"   ⚠️ Recommendation generation failed: {response_data['error']}")
                return {
                    "error": response_data["error"],
                    "recommendation_status": "failed"
                }
            print(f"   ✅ Recommendation generated successfully")
            return {
                "recommendation": response_data,
                "recommendation_status": "completed"
            }
        except Exception as e:
            print(f"   ⚠️ Unexpected error in recommendation generation: {e}")
            return {
                "error": str(e),
                "recommendation_status": "failed"
            }