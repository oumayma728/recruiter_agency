from typing import Dict, Any
from .base_agent import BaseAgent
class ProfileEnhancerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Profile Enhancer",
            instructions=(
                """Enhance the candidate's profile by:
                1. Adding relevant skills based on job descriptions
                2. Highlighting key achievements
                3. Structuring the profile for better readability
                Provide an enhanced profile summary."""
            )
        )
    async def run(self, messages: list) -> Dict[str, Any]:
        print(f"💡 {self.name}: Enhancing candidate profile...")
        try:
            last_message = messages[-1]["content"]
            data = last_message if isinstance(last_message, dict) else {}
            extraction = data.get("extraction_results", {})
            skills = extraction.get("skills", [])
            experience = extraction.get("experience", [])
            achievements = extraction.get("achievements", [])

            enhancement_prompt = f"""
                Based on the candidate data below, generate professional recommendations 
                to improve their profile.

                SKILLS: {skills[:10]}
                EXPERIENCE: {experience[:3]}
                ACHIEVEMENTS: {achievements[:3]}

                Return JSON format:
                {{
                    "recommendations": [
                        "Recommendation 1",
                        "Recommendation 2",
                        "Recommendation 3"
                    ]
                }}
                """.strip()
            print(f"   🧠 Generating enhanced profile with prompt:\n{enhancement_prompt}\n")
            response = self._query_ollama(enhancement_prompt)
            response_data = self._parse_json_safely(response)
            if "error" in response_data:
                print(f"   ⚠️ Profile enhancement failed: {response_data['error']}")
                return {
                    "error": response_data["error"],
                    "enhancement_status": "failed"
                }
            return{
                "enhanced_profile": response_data.get("enhanced_profile", ""),
                "enhancement_status": "success"
            }
        except Exception as e:
            print(f"   ❌ Error during profile enhancement: {str(e)}")
            return {
                "error": str(e),
                "enhancement_status": "failed"
            }