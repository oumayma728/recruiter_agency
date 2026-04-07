from typing import Dict, Any
from .base_agent import BaseAgent
import json

class ProfileEnhancerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Profile Enhancer",
            instructions="""Enhance candidate profiles with actionable recommendations."""
        )
    
    async def run(self, messages: list) -> Dict[str, Any]:
        print(f"💡 {self.name}: Enhancing candidate profile...")
        
        try:
            last_message = messages[-1]["content"]
            data = json.loads(last_message) if isinstance(last_message, str) else last_message
            
            # NEW: Skip enhancement if profile is already strong
            if self._is_profile_strong_enough(data):
                print(f"   ⏭️ Profile already strong, skipping enhancement")
                return {"recommendations": [], "enhancement_status": "skipped"}
            
            # Extract data more cleanly
            profile = data.get("structured_data", data)
            skills = profile.get("skills", {}).get("technical", [])
            years = profile.get("analysis", {}).get("years_of_experience", 0)
            achievements = profile.get("analysis", {}).get("key_achievements", [])
            
            # Only enhance if there are obvious gaps
            gaps = self._identify_gaps(skills, years, achievements)
            if not gaps:
                return {"recommendations": [], "enhancement_status": "no_gaps_found"}
            
            # Single, focused LLM call
            prompt = self._build_enhancement_prompt(skills, years, achievements, gaps)
            response = self._query_ollama(prompt)
            result = self._parse_json_safely(response)
            
            return {
                "recommendations": result.get("recommendations", []),
                "identified_gaps": gaps,
                "enhancement_status": "success"
            }
            
        except Exception as e:
            return {"error": str(e), "enhancement_status": "failed"}
    
    def _is_profile_strong_enough(self, data: Dict) -> bool:
        """Skip enhancement if candidate already has 10+ skills and 3+ achievements"""
        profile = data.get("structured_data", data)
        skills = profile.get("skills", {}).get("technical", [])
        achievements = profile.get("analysis", {}).get("key_achievements", [])
        
        return len(skills) >= 10 and len(achievements) >= 3
    
    def _identify_gaps(self, skills: list, years: float, achievements: list) -> list:
        """Identify specific gaps without LLM"""
        gaps = []
        if len(skills) < 5:
            gaps.append("limited_technical_skills")
        if years < 2:
            gaps.append("entry_level_experience")
        if len(achievements) < 2:
            gaps.append("missing_quantifiable_achievements")
        return gaps