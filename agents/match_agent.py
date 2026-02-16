from .base_agent import BaseAgent
import json
class MatchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="MatchAgent",
            instructions="""Match candidate profiles with job positions.
            Consider: skills match, experience level, location preferences.
            Provide detailed reasoning and compatibility scores.
            Return matches in JSON format with title, match_score, and location fields.""",
        )
    async def run(self,messages:list) -> dict:
        try:
            last_message = messages[-1]["content"]
            # Ensure dict
            if isinstance(last_message, str):
                data = json.loads(last_message)
            else:
                data = last_message

            candidate_profile = data.get("candidate_profile")
            job_position = data.get("job_position")

            if not candidate_profile or not job_position:
                return {"error": "Missing candidate_profile or job_position", "match_status": "failed"}

            match_prompt = f"""Compare this candidate against this job.

                Candidate Profile:
                {json.dumps(candidate_profile, indent=2)}
                Job Position:
                {json.dumps(job_position, indent=2)}
                Return ONLY valid JSON (no other text):
                {{
                "match_score": 0-100,
                "skills_match": {{
                    "matched": ["skill1", "skill2"],
                    "missing": ["skill3"]
                }},
                "experience_match": true/false,
                "recommendation": "YES/NO/MAYBE",
                "reasoning": "brief explanation",
                "strengths": ["point1", "point2"],
                "concerns": ["point1", "point2"]
                }}
                Be objective, concise, and professional. Do not invent skills or experience.
                """
            # Here you would call your LLM with the match_prompt and the candidate/job data
            match_response = self._query_ollama(match_prompt)
            # Parse the response and return structured data
            parsed_response=self._parse_json_safely(match_response)
            if "error" in parsed_response:
                return {
                    "error": f"Failed to parse AI response: {parsed_response['error']}",
                    "raw_ai_response": match_response,
                    "match_status": "failed"
                }
            #validate response
            if not self._validate_match_response(parsed_response):
                return {
                    "error": "Parsed match response is invalid or incomplete",
                    "ai_response": match_response,
                    "match_status": "failed"
                }
            return {
                "match_analysis": parsed_response,
                "match_status": "completed"
            }
        except Exception as e:
            return {"error": str(e), "match_status": "failed"}
                            