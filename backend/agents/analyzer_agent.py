import json
from typing import Any, Dict
from .base_agent import BaseAgent

class AnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Analyzer",
            instructions=("""You are an expert HR analyst. You analyze:
            1. Resumes/CVs - to extract skills, experience, education
            2. Job descriptions - to classify domain, seniority, strengths
            Return ONLY valid JSON, no explanations."""),
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        print(f"🔍 {self.name}: Starting analysis...")

        try:
            last_message = messages[-1]["content"]

            # Convert input to dict if it's a string
            if isinstance(last_message, str):
                data = json.loads(last_message)
            else:
                data = last_message

            # Check if this is a job description (from evaluation)
            if "job_description" in data:
                print(f"   📋 Analyzing job description...")
                return await self._analyze_job_description(data)
            
            # Check if this is a resume/CV (from ExtractorAgent)
            elif "structured_data" in data or "raw_text" in data:
                print(f"   📄 Analyzing resume/CV...")
                return await self._analyze_resume(data)
            
            else:
                return {
                    "error": "Unknown input format. Expected 'job_description', 'structured_data', or 'raw_text'",
                    "analysis_status": "failed"
                }
            
        except Exception as e:
            return {"error": str(e), "analysis_status": "failed"}

    async def _analyze_job_description(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a job description for domain, seniority, and strengths"""
        
        # Extract job description text
        job_text = data.get("job_description", "")
        
        # If job_description is a dict (from scraper), extract relevant fields
        if isinstance(job_text, dict):
            title = job_text.get("title", "")
            description = job_text.get("description", "")
            requirements = job_text.get("requirements", "")
            job_text = f"{title}\n{description}\n{requirements}"
        
        if not job_text or job_text.strip() == "":
            return {
                "domain": "technology",
                "seniority": "Mid",
                "strengths": [],
                "analysis_status": "failed",
                "error": "No job description text found"
            }
        
        print(f"   Analyzing job: {job_text[:100]}...")
        
        # Prompt for job analysis
        prompt = f"""
        Analyze this job description and return ONLY valid JSON:
        
        Classify:
        1. domain: Choose ONE from:
           - technology (software, development, engineering, programming)
           - marketing (digital marketing, SEO, social media, content)
           - sales (B2B, account management, business development)
           - finance (accounting, financial analysis, investment)
           - operations (project management, supply chain, logistics)
           - hr (recruitment, talent management, people operations)
           - design (UI/UX, graphic design, product design)
           - data (data science, analytics, BI, machine learning)
        
        2. seniority: Choose ONE from:
           - Junior (0-2 years experience)
           - Mid (2-5 years experience)
           - Senior (5+ years experience)
        
        3. strengths: List the top 3-5 key skills/strengths required
        
        Job Description:
        {job_text}
        
        Return ONLY this JSON format (no other text):
        {{
            "domain": "technology",
            "seniority": "Mid",
            "strengths": ["Python", "React", "AWS"]
        }}
        """
        
        response = self._query_ollama(prompt)
        analysis = self._parse_json_safely(response)
        
        # Fallback if parsing fails
        if "error" in analysis:
            print(f"   ⚠️ JSON parsing failed, using fallback")
            analysis = {
                "domain": self._guess_domain(job_text),
                "seniority": self._guess_seniority(job_text),
                "strengths": self._extract_key_strengths(job_text)
            }
        
        print(f"   ✅ Domain: {analysis.get('domain')}, Seniority: {analysis.get('seniority')}")
        
        return {
            "domain": analysis.get("domain", "technology"),
            "seniority": analysis.get("seniority", "Mid"),
            "strengths": analysis.get("strengths", []),
            "analysis_status": "completed",
            "confidence_score": 0.85
        }

    async def _analyze_resume(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a resume/CV (your existing logic)"""
        
        # Get resume text from either structured_data or raw_text
        structured = data.get("structured_data")
        raw_text = data.get("raw_text")
        
        # Use structured data if available, otherwise use raw text
        if structured:
            resume_input = structured
            print(f"   Using structured data from ExtractorAgent")
        elif raw_text:
            resume_input = raw_text
            print(f"   Using raw text from ExtractorAgent")
        else:
            return {"error": "No structured_data or raw_text found", "analysis_status": "failed"}

        # Convert structured data to string if it's a dict
        if isinstance(resume_input, dict):
            resume_input = json.dumps(resume_input, indent=2)

        print(f"   Extracting skills...")
        skills_prompt = f"""
        Extract ALL technical skills, tools, databases, and AI technologies from this resume.
        Look in every section: skills, experience, projects, education.
        
        CATEGORIES:
            1. technical_skills = Programming languages and frameworks
            2. tools = Development and collaboration tools (NOT programming)
            3. databases = Database systems ONLY
            4. ai_ml_skills = AI/ML technologies and libraries
        
        IMPORTANT RULES:
        - Look in EVERY section
        - Extract EVERYTHING, don't stop at 5 items
        - Internships count as experience
        
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
        
        print(f"   Analyzing experience...")
        experience_prompt = f"""
        Analyze work experience from this resume.

        IMPORTANT RULES:
        - Count ONLY PROFESSIONAL work experience (full-time jobs, part-time jobs)
        - Internships (stage) count as 0.5 years each, max 1 year total
        - Projects and education do NOT count as experience
        - Convert all dates to years

        Examples:
        - 6-month internship = 0.5 years
        - 1 year full-time job = 1 year
        - 2 internships (6 months each) = 1 year total

        Return only this JSON:
        {{
            "years_of_experience": 0.0,
            "experience_level": "Junior/Mid/Senior"
        }}

        EXPERIENCE LEVEL CLASSIFICATION:
        - Junior: 0-2 years (including internships)
        - Mid: 2-5 years (professional experience only)
        - Senior: 5+ years (professional experience only)

        Resume data:
        {resume_input}
        """
        
        experience_response = self._query_ollama(experience_prompt)
        experience_data = self._parse_json_safely(experience_response)
        if "error" in experience_data:
            experience_data = {"years_of_experience": 0, "experience_level": "Junior"}
        
        years = experience_data.get("years_of_experience", 0)
        if years < 2:
            experience_data["experience_level"] = "Junior"
        elif years <= 5:
            experience_data["experience_level"] = "Mid"
        else:
            experience_data["experience_level"] = "Senior"

        print(f"   Extracting education...")
        edu_prompt = f"""
        Extract education background from this resume.
        Return only this JSON:
        {{
            "education": [
                {{
                    "degree": "",
                    "field": "",
                    "institution": "",
                    "year": 0
                }}
            ]
        }}
        
        Resume:
        {resume_input}
        """
        
        edu_response = self._query_ollama(edu_prompt)
        edu_data = self._parse_json_safely(edu_response)
        if "error" in edu_data:
            edu_data = {"education": []}
        
        print(f"   Identifying achievements...")
        domain_prompt = f"""
        Based on this resume's projects and experience, identify:
        1. Key achievements (what did they build/accomplish?)
        2. Domain expertise (what areas do they work in?)
        
        Return ONLY this JSON:
        {{
            "key_achievements": [],
            "domain_expertise": []
        }}
        
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

    def _guess_domain(self, job_text: str) -> str:
        """Fallback: guess domain from keywords"""
        text_lower = job_text.lower()
        
        domain_keywords = {
            "technology": ["software", "developer", "engineer", "programming", "code", "api", "full-stack", "frontend", "backend"],
            "marketing": ["marketing", "seo", "social media", "content", "campaign", "brand"],
            "sales": ["sales", "business development", "account executive", "client"],
            "finance": ["finance", "accounting", "budget", "forecast", "financial"],
            "operations": ["operations", "project management", "logistics", "supply chain"],
            "hr": ["hr", "human resources", "recruitment", "talent", "people"],
            "design": ["design", "ui", "ux", "figma", "photoshop"],
            "data": ["data", "analytics", "bi", "machine learning", "sql"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return domain
        
        return "technology"

    def _guess_seniority(self, job_text: str) -> str:
        """Fallback: guess seniority from keywords"""
        text_lower = job_text.lower()
        
        if any(word in text_lower for word in ["senior", "lead", "principal", "staff", "experienced", "5+"]):
            return "Senior"
        elif any(word in text_lower for word in ["junior", "entry", "associate", "trainee", "0-2"]):
            return "Junior"
        else:
            return "Mid"

    def _extract_key_strengths(self, job_text: str) -> list:
        """Fallback: extract key skills from job description"""
        common_skills = [
            "Python", "JavaScript", "Java", "React", "Angular", "Vue", "Node.js",
            "AWS", "Docker", "Kubernetes", "SQL", "MongoDB", "PostgreSQL",
            "Machine Learning", "AI", "Data Science", "DevOps", "Agile",
            "Project Management", "Leadership", "Communication"
        ]
        
        found_skills = []
        for skill in common_skills:
            if skill.lower() in job_text.lower():
                found_skills.append(skill)
        
        return found_skills[:5]

    def _validate_analysis(self, data: Dict[str, Any]) -> bool:
        """Validates resume analysis structure"""
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

    def _calculate_confidence(self, data: Dict[str, Any]) -> float:
        """Calculates confidence score for resume analysis"""
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
        if education and isinstance(education, list) and len(education) > 0:
            confidence += 0.15
        if data.get("experience_level") in ["Junior", "Mid", "Senior"]:
            confidence += 0.15
        if data.get("key_achievements"):
            confidence += 0.15
        if data.get("domain_expertise"):
            confidence += 0.10
        
        return round(confidence, 2)