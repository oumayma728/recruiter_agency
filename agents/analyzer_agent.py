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

            print(f"pass 1: Extracting skills...")
            skills_prompt=f"""
            Extract ALL technical skills, tools, databases, and AI technologies from this resume.
            Look in every section: skills, experience, projects, education.
            CATEGORIES (be precise):

                1. technical_skills = Programming languages and frameworks
                Examples: C#, Python, JavaScript, React.js, React Native, Node.js, ASP.NET, NestJS, Next.js, TypeScript

                2. tools = Development and collaboration tools (NOT programming)
                Examples: Git/GitHub, Docker, Android Studio, Power Platform, MQTT, SignalR

                3. databases = Database systems ONLY
                Examples: MongoDB, PostgreSQL, SQL Server, Oracle, MySQL

                4. ai_ml_skills = AI/ML technologies and libraries
                Examples: TensorFlow, PyTorch, OpenAI API, Keras, scikit-learn

                IMPORTANT RULES:
                - Look in EVERY section: Skills, Projects, Experience
                - NestJS and Next.js are FRAMEWORKS → technical_skills
                - MQTT and SignalR are TOOLS → tools  
                - MongoDB and PostgreSQL are DATABASES → databases
                - Extract EVERYTHING, don't stop at 5 items

                Return ONLY this JSON:
                {{
                "technical_skills": [],
                "tools": [],
                "databases": [],
                "ai_ml_skills": []
                }}

            Resume:
            {resume_input}
            """
            skills_response = self._query_ollama(skills_prompt)
            skills_data = self._parse_json_safely(skills_response)
            if "error" in skills_data:
                skills_data = {"technical_skills": [], "tools": [], "databases": [], "ai_ml_skills": []}
            print(f"Pass2: Analyzing experience and education...")
            experience_prompt = f"""
            Analyze work experience from this resume
            Count Only PROFESSIONAL work experience (ignore education/internship time)
            Return only this JSON:
            {{
            years_of_experience: 0,
            experience_level: "Junior/Mid/Senior",
            }}
            EXPERIENCE LEVEL CLASSIFICATION (STRICT):
            - Junior: 0-2 years of PROFESSIONAL work experience (ignore education/internship time)
            - Mid: 2-5 years of professional work experience
            - Senior: 5+ years of professional work experience

            IMPORTANT RULES:
            - years_of_experience = ONLY count actual work/internship months (NOT education years)
            - A 6-month internship = 0.5 years of experience → Junior
            - University time does NOT count as work experience
            - Projects during education do NOT count as professional experience
                        Resume:
            {resume_input}
            """
            experience_response = self._query_ollama(experience_prompt)
            experience_data = self._parse_json_safely(experience_response)
            if "error" in experience_data:
                experience_data = {"years_of_experience": 0, "experience_level": "Junior"}
            years = experience_data.get("years_of_experience", 0)
            if years < 2:
                experience_data["experience_level"] = "Junior"
            elif years < 5:
                experience_data["experience_level"] = "Mid"
            else:
                experience_data["experience_level"] = "Senior"

            print(f"Pass3: Extracting analysis...")
            edu_prompt=f"""
            Extract education background and key achievements from this resume.
            Return only this JSON:
            {{
            "education":[
            {{
                "degree": "",
                "field": "",
                "institution": "",  
                "year": 0

            }}]
            }}
            resume:
            {resume_input}
            """
            edu_response = self._query_ollama(edu_prompt)
            edu_data = self._parse_json_safely(edu_response)
            if "error" in edu_data:
                edu_data = {"education": []}
            print(f"Pass4: identifying key achievements...")
            domain_prompt=f"""
                        Based on this resume's projects and experience, identify:
            1. Key achievements (what did they build/accomplish?)
            2. Domain expertise (what areas do they work in?)

            Return ONLY this JSON:
            {{
            "key_achievements": [],
            "domain_expertise": []
            }}

            Examples of domain_expertise:
            - Projects involve IoT → "IoT Platforms"
            - Projects use React Native → "Mobile Development"
            - Projects use MERN stack → "Full-Stack Development"
            - Projects use TensorFlow → "AI Integration"

            Resume:
            {resume_input}
            """
            domain_response = self._query_ollama(domain_prompt)
            domain_data = self._parse_json_safely(domain_response)
            if "error" in domain_data:
                domain_data = {"key_achievements": [], "domain_expertise": []}
            
            parsed_data = {
                **skills_data,
                **experience_data,
                **edu_data,
                **domain_data
            }
            if not self._validate_analysis(parsed_data):
                print(f"   ⚠️ Analysis data failed validation")
                return {
                    "error": "Parsed analysis data is invalid or incomplete",
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
            "tools",
            "databases",
            "ai_ml_skills",
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
        if not isinstance(data["tools"], list):
            return False
        if not isinstance(data["databases"], list):
            return False
        if not isinstance(data["ai_ml_skills"], list):
            return False
        if not isinstance(data["years_of_experience"], (int, float)):
            return False
        if not isinstance(data["education"], list):
            return False
        valid_levels = ["Junior", "Mid", "Senior"]
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
        if data.get("tools"):
            confidence += 0.10
        if data.get("databases"):
            confidence += 0.10
        if data.get("ai_ml_skills"):
            confidence += 0.10
        if data.get("years_of_experience", 0) > 0:
            confidence += 0.20
        education = data.get("education", {})
        if education and isinstance(education, list):
            confidence += 0.15
        if data.get("experience_level") in ["Junior", "Mid", "Senior"]:
            confidence += 0.15
        if data.get("key_achievements"):
            confidence += 0.15
        if data.get("domain_expertise"):
            confidence += 0.10

        return round(confidence, 2)