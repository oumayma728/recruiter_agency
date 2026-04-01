import json
from typing import Dict, Any
from .base_agent import BaseAgent


class RecommenderAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Recommender",
            instructions="""Generate final recommendations considering:
            1. Extracted profile
            2. Skills analysis
            3. Job matches
            4. Screening results
            Provide clear next steps and specific recommendations.""",
        )
    
    async def run(self, messages: list) -> Dict[str, Any]:
        print(f"💡 {self.name}: Generating final recommendations...")
        
        try:
            last_message = messages[-1]["content"]
            data = json.loads(last_message) if isinstance(last_message, str) else last_message

            # Extract data
            extraction = data.get("extraction_results", {})
            analysis = data.get("analysis_results", {})
            matches = data.get("match_results", {})

            skills_analysis = analysis.get("skills_analysis", {})
            matched_jobs = matches.get("matched_jobs", [])

            # DEBUG
            print(f"   🔍 Skills analysis available: {bool(skills_analysis)}")
            print(f"   🔍 Matched jobs count: {len(matched_jobs)}")

            # If no data, use fallback
            if not skills_analysis:
                print("   ⚠️ No skills analysis - using fallback")
                return {
                    "recommendation": self._generate_fallback(),
                    "recommendation_status": "completed"
                }

            # Build prompt
            recommendation_prompt = f"""
Analyze this candidate and return ONLY valid JSON.

CANDIDATE:
Technical Skills: {skills_analysis.get('technical_skills', [])[:10]}
Experience: {skills_analysis.get('years_of_experience', 0)} years
Level: {skills_analysis.get('experience_level', 'Unknown')}

TOP JOBS:
{json.dumps(matched_jobs[:2], indent=2) if matched_jobs else "No matches"}

Return ONLY this JSON (no markdown, no other text):
{{
  "overall_assessment": "brief summary",
  "hiring_recommendation": "PROCEED or CONSIDER or PASS",
  overall_assessment": "brief summary",
  "confidence_level": "high or medium or low",
  "top_match_analysis": {{
    "best_job": "job title",
    "match_reasoning": "why",
    "salary_recommendation": "range"
  }},
  "strengths": ["strength1", "strength2"],
  "concerns": ["concern1"],
  "next_steps": ["step1", "step2"],
  "interview_questions": ["q1", "q2"]
}}
""".strip()

            print(f"   🤖 Querying AI ({len(recommendation_prompt)} chars)")
            
            response = self._query_ollama(recommendation_prompt)
            
            # DEBUG AI RESPONSE
            print(f"   🔍 AI response type: {type(response)}")
            print(f"   🔍 AI response length: {len(response) if response else 0}")
            
            if not response or len(str(response).strip()) < 20:
                print("   ⚠️ AI returned empty/short response - using fallback")
                return {
                    "recommendation": self._generate_fallback(),
                    "recommendation_status": "completed"
                }
            
            
            response_data = self._parse_json_safely(response)
            
            if "error" in response_data:
                print(f"   ⚠️ JSON parsing failed: {response_data['error']}")
                print("   Using fallback recommendation")
                return {
                    "recommendation": self._generate_fallback(),
                    "recommendation_status": "completed"
                }
            
            # VALIDATE required fields
            required_fields = [
                "overall_assessment",
                "hiring_recommendation",
                "confidence_level",
                "strengths",
                "concerns",
                "next_steps",
                "interview_questions"
            ]
            
            missing_fields = [f for f in required_fields if f not in response_data]
            
            if missing_fields:
                print(f"   ⚠️ Missing fields: {missing_fields}")
                print("   Using fallback recommendation")
                return {
                    "recommendation": self._generate_fallback(),
                    "recommendation_status": "completed"
                }
            
            print(f"   ✅ Recommendation generated successfully")
            
            return {
                "recommendation_status": "completed"
            }
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return {
                "recommendation": self._generate_fallback(),
                "recommendation_status": "completed"
            }

    def _generate_fallback(self) -> Dict[str, Any]:
        """Generate basic fallback recommendation"""
        return {
            "overall_assessment": "Candidate profile processed successfully. Manual review recommended for detailed assessment.",
            "hiring_recommendation": "CONSIDER",
            "confidence_level": "medium",
            "top_match_analysis": {
                "best_job": "See matched jobs section",
                "match_reasoning": "Multiple factors to consider",
                "salary_recommendation": "Based on market standards"
            },
            "strengths": [
                "Profile successfully extracted and analyzed",
                "Job matches identified"
            ],
            "concerns": [
                "Automated recommendation unavailable - manual review needed"
            ],
            "next_steps": [
                "Review candidate profile manually",
                "Assess matched job opportunities",
                "Schedule interview if qualified"
            ],
            "interview_questions": [
                "Walk me through your experience with the key technologies",
                "Describe a challenging project you've worked on",
                "What interests you about this role?"
            ]
        }