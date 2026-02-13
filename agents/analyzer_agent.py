import json
from typing import Any, Dict
from .base_agent import BaseAgent

class AnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Analyzer",
            instructions=("""You are an expert HR analyst specializing in technical recruitment.
            Analyze resumes to extract:
            - Technical skills and proficiency levels
            - Years of relevant experience
            - Education background
            - Career trajectory (Junior/Mid/Senior)
            - Notable achievements
            - Domain expertise areas

            Be objective and data-driven. Return ONLY valid JSON, no explanations."""            ),
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        print(f"🔍 {self.name}: Starting analysis...")  # ← ADD THIS

        try:
            last_message = messages[-1]["content"]

            # Ensure dict
            if isinstance(last_message, str):
                data = json.loads(last_message)
            else:
                data = last_message

            structured = data.get("structured_data")
            raw_text = data.get("raw_text")

            # Pick best input
            resume_input = structured if structured else raw_text
            if not resume_input:
                return {"error": "No structured_data or raw_text found", "analysis_status": "failed"}

            analysis_prompt = f"""
Return ONLY valid JSON with this structure:
{{
  "technical_skills": [],
  "years_of_experience": 0,
  "education": {{"level": "", "field": ""}},
  "experience_level": "Junior/Mid-level/Senior",
  "key_achievements": [],
  "domain_expertise": []
}}

Resume data:
{resume_input}
""".strip()

            analysis_response = self._query_ollama(analysis_prompt)

            # Parse AI JSON
            parsed_data = self._parse_json_safely(analysis_response)

            if "error" in parsed_data:
                print(f"   ⚠️ Failed to parse AI response: {parsed_data['error']}")
                return {
                    "error": f"Failed to parse AI response: {parsed_data['error']}",
                    "raw_ai_response": analysis_response,
                    "analysis_status": "failed",
                    "confidence_score": 0.0
                }
            if not self._validate_analysis(parsed_data):
                print(f"   ⚠️ Analysis data failed validation")
                return {
                    "error": "Parsed analysis data is invalid or incomplete",
                    "ai_response": analysis_response,
                    "analysis_status": "failed"
                }
            confidence = self._calculate_confidence(parsed_data)
            print(f"   ✅ Analysis complete with {confidence:.0%} confidence")
            return {
                "skills_analysis": parsed_data,
                "analysis_status": "completed",
                "confidence_score": confidence
            }
            


        except Exception as e:
            return {"error": str(e), "analysis_status": "failed"}
    def _validate_analysis(self,data:Dict[str,Any]) -> bool:
        """
        Validates the structure of the analysis data.
        """
        required_keys = [
            "technical_skills",
            "years_of_experience",
            "education",
            "experience_level",
            "key_achievements",
            "domain_expertise"
        ]
        if not all(key in data for key in required_keys):
            return False

        #validate types
        if not isinstance(data["technical_skills"], list):
            return False
        if not isinstance(data["years_of_experience"], (int, float)):
            return False
        if not isinstance(data["education"], dict):
            return False
        valid_levels = ["Junior", "Mid-level", "Senior"]
        if data["experience_level"] not in valid_levels:
            return False
        
        return True
    def _calculate_confidence(self,data:Dict[str,Any]) -> float:
        """
        Calculates a confidence score based on the completeness of the analysis data.
        """
        confidence = 0.0

        if data.get("technical_skills"):
            confidence += 0.25
        if data.get("years_of_experience", 0) > 0:
            confidence += 0.20
        education = data.get("education", {})
        if education.get("level") and education.get("field"):
            confidence += 0.15
        if data.get("experience_level") in ["Junior", "Mid-level", "Senior"]:
            confidence += 0.15
        if data.get("key_achievements"):
            confidence += 0.15
        if data.get("domain_expertise"):
            confidence += 0.10

        return round(confidence, 2)