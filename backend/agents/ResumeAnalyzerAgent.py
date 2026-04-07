import json
import re
from datetime import datetime
from typing import Dict, Any, List
from pdfminer.high_level import extract_text
from .base_agent import BaseAgent

class ResumeAnalyzerAgent(BaseAgent):
    """
    Merged Extractor + Analyzer Agent.
    Extracts structured data AND analyzes candidate profile in ONE pass
    """
    
    def __init__(self):
        super().__init__(
            name="ResumeAnalyzer",
            instructions=("""You are an expert HR analyst and resume extractor.
Extract AND analyze resumes in one pass. Return ONLY valid JSON."""),
        )
    
    # ========== DATE UTILITIES (from ExtractorAgent) ==========
    def _calculate_years_of_experience(self, experience_list: list) -> float:
        """Calculate total years from experience entries (deterministic)"""
        total_months = 0
        internship_keywords = ["stage", "stagiaire", "intern", "internship", "trainee", "apprenti"]
        
        for exp in experience_list:
            start = exp.get("start_date", "")
            end = exp.get("end_date", "")

            title = (exp.get("title", "") or "").lower()

            try:
                start_parsed = self._parse_month_year(start) if start else None
                end_parsed = self._parse_month_year(end) if end else None

                if start_parsed and not end_parsed:
                    # Treat "depuis/since/from" as ongoing when end date is missing.
                    start_text = str(start).lower()
                    if re.search(r"\b(depuis|since|from)\b", start_text):
                        now = datetime.now()
                        end_parsed = (now.year, now.month)

                if start_parsed and end_parsed:
                    start_year, start_month = start_parsed
                    end_year, end_month = end_parsed
                    
                    months_diff = (end_year - start_year) * 12 + (end_month - start_month)
                    if months_diff <= 0:
                        months_diff = 1
                else:
                    months_diff = self._extract_duration_months(exp)
                    if months_diff <= 0:
                        continue

                if any(keyword in title for keyword in internship_keywords):
                    months_diff = min(months_diff, 6)
                
                total_months += max(0, months_diff)
                
            except Exception as e:
                print(f"   ⚠️ Date parsing error: {start} - {end} -> {e}")
                continue
        
        return round(total_months / 12, 1)

    def _extract_duration_months(self, exp: dict) -> int:
        """Fallback duration parser for entries like 'stage 6 mois' when dates are missing."""
        if not isinstance(exp, dict):
            return 0

        text_chunks = [
            str(exp.get("title", "") or ""),
            str(exp.get("company", "") or ""),
            " ".join(exp.get("responsibilities", []) or []),
            str(exp.get("description", "") or ""),
        ]
        text = " ".join(text_chunks).lower()

        month_match = re.search(r"(\d{1,2})\s*(mois|month|months)\b", text)
        if month_match:
            return int(month_match.group(1))

        year_match = re.search(r"(\d+(?:[\.,]\d+)?)\s*(an|ans|année|années|year|years)\b", text)
        if year_match:
            years = float(year_match.group(1).replace(",", "."))
            return max(1, int(round(years * 12)))

        return 0

    def _parse_month_year(self, value: str):
        """Parse common CV date formats into (year, month)."""
        if not value or not isinstance(value, str):
            return None

        raw = value.strip().lower()
        if not raw:
            return None

        raw = re.sub(r"^(depuis|since|from)\s+", "", raw)

        if raw in {"present", "présent", "now", "current", "ongoing", "today", "actuel", "en cours"}:
            now = datetime.now()
            return now.year, now.month

        mm_yyyy = re.search(r"\b(\d{1,2})\s*/\s*(\d{4})\b", raw)
        if mm_yyyy:
            month = int(mm_yyyy.group(1))
            year = int(mm_yyyy.group(2))
            if 1 <= month <= 12:
                return year, month

        yyyy_mm = re.search(r"\b(\d{4})\s*[-/]\s*(\d{1,2})\b", raw)
        if yyyy_mm:
            year = int(yyyy_mm.group(1))
            month = int(yyyy_mm.group(2))
            if 1 <= month <= 12:
                return year, month

        year_only = re.search(r"\b(19|20)\d{2}\b", raw)
        if year_only:
            return int(year_only.group(0)), 1

        months = {
            "jan": 1, "january": 1, "janv": 1, "janvier": 1,
            "feb": 2, "february": 2, "fev": 2, "fevrier": 2,
            "mar": 3, "march": 3, "mars": 3,
            "apr": 4, "april": 4, "avr": 4, "avril": 4,
            "may": 5, "mai": 5,
            "jun": 6, "june": 6, "juin": 6,
            "jul": 7, "july": 7, "juil": 7, "juillet": 7,
            "aug": 8, "august": 8, "aou": 8, "aout": 8,
            "sep": 9, "sept": 9, "september": 9,
            "oct": 10, "october": 10,
            "nov": 11, "november": 11,
            "dec": 12, "december": 12, "decembre": 12,
        }

        month_match = re.search(r"([a-zA-Zéèêàâùûôîïç]+)", raw)
        year_match = re.search(r"\b(19|20)\d{2}\b", raw)
        if month_match and year_match:
            token = month_match.group(1).lower()
            for key, month in months.items():
                if token.startswith(key):
                    return int(year_match.group(0)), month

        return None
    
    def _determine_experience_level(self, years: float) -> str:
        if years < 2:
            return "Junior"
        elif years <= 5:
            return "Mid"
        else:
            return "Senior"
    
    def _normalize_date_value(self, value: str) -> str:
        """Normalize date values"""
        if not value or not isinstance(value, str):
            return ""
        
        cleaned = value.strip()
        lower = cleaned.lower()

        lower = re.sub(r"^(depuis|since|from)\s+", "", lower)
        cleaned = re.sub(r"^(depuis|since|from)\s+", "", cleaned, flags=re.IGNORECASE).strip()
        
        if lower in ["present", "présent", "now", "current", "ongoing", "today", "actuel", "en cours"]:
            return "Present"

        if re.match(r"^\d{4}$", cleaned):
            return f"01/{cleaned}"
        
        if re.match(r"^\d{1,2}/\d{4}$", cleaned):
            month, year = cleaned.split("/")
            return f"{int(month):02d}/{year}"
        
        match = re.match(r"^(\d{4})[-/](\d{1,2})$", cleaned)
        if match:
            year, month = match.groups()
            return f"{int(month):02d}/{year}"
        
        return cleaned
    
    def _extract_date_ranges_from_text(self, text: str) -> list:
        """Extract date ranges from raw text"""
        if not text:
            return []
        
        normalized_text = text.replace("\u2013", "-").replace("\u2014", "-")
        
        month_names = (
            "jan|january|janv|janvier|feb|february|fev|fevrier|mar|march|mars|apr|april|avr|avril|"
            "may|mai|jun|june|juin|jul|july|juil|juillet|aug|august|aou|aout|sep|sept|september|"
            "oct|october|nov|november|dec|december|decembre"
        )
        
        date_patterns = [
            rf"\b(\d{{1,2}}/\d{{4}})\s*[-–—]\s*(\d{{1,2}}/\d{{4}}|present|now|current|ongoing|today)\b",
            rf"\b(?:{month_names})\s+\d{{4}}\s*[-–—]\s*(?:{month_names})\s+\d{{4}}\b",
            rf"\b(?:{month_names})\s+\d{{4}}\s*[-–—]\s*(?:present|now|current|ongoing|today)\b",
            r"\b(\d{4})\s*[-–—]\s*(\d{4}|present|now|current|ongoing|today)\b",
            r"\b(depuis|since|from)\s+(\d{4})\b",
        ]
        
        ranges = []
        for pattern in date_patterns:
            for match in re.finditer(pattern, normalized_text, flags=re.IGNORECASE):
                raw_range = match.group(0)
                parts = re.split(r"\s*[-–—]\s*", raw_range)
                if len(parts) != 2:
                    from_match = re.search(r"\b(?:depuis|since|from)\s+(\d{4})\b", raw_range, flags=re.IGNORECASE)
                    if from_match:
                        parts = [from_match.group(1), "Present"]
                    else:
                        continue
                
                start = self._normalize_date_value(parts[0])
                end = self._normalize_date_value(parts[1])
                
                ranges.append((start, end))
        
        unique_ranges = []
        seen = set()
        for start, end in ranges:
            key = (start, end)
            if key not in seen:
                seen.add(key)
                unique_ranges.append({"start_date": start, "end_date": end})
        
        return unique_ranges
    
    def _backfill_experience_dates(self, experience_list: list, raw_text: str) -> list:
        """Fill missing experience dates from raw text"""
        if not isinstance(experience_list, list):
            return experience_list

        date_ranges = self._extract_date_ranges_from_text(raw_text)
        
        filled = []
        range_index = 0
        for exp in experience_list:
            if not isinstance(exp, dict):
                filled.append(exp)
                continue
            
            start = (exp.get("start_date") or "").strip()
            end = (exp.get("end_date") or "").strip()

            # Normalize already extracted dates
            if start:
                exp["start_date"] = self._normalize_date_value(start)
            if end:
                exp["end_date"] = self._normalize_date_value(end)

            # Common CV form: "depuis 2020" with missing end date
            if (not end) and re.search(r"\b(depuis|since|from)\b", start, flags=re.IGNORECASE):
                exp["end_date"] = "Present"
                end = "Present"

            # If start is just a year with no end date, treat as ongoing by default.
            if (not end) and start and re.fullmatch(r"\d{4}|\d{2}/\d{4}", exp.get("start_date", "")):
                exp["end_date"] = "Present"
                end = "Present"
            
            if (not start or not end) and range_index < len(date_ranges):
                inferred = date_ranges[range_index]
                range_index += 1
                
                if not start:
                    exp["start_date"] = inferred["start_date"]
                if not end:
                    exp["end_date"] = inferred["end_date"]
            
            filled.append(exp)
        
        return filled
    
    # ========== JOB TITLE UTILITIES (fixed for Data Analyst) ==========
    def _normalize_job_title(self, value: str) -> str:
        """Normalize job title (preserve original case for data roles)"""
        if not value or not isinstance(value, str):
            return ""
        
        cleaned = value.strip()
        
        # Don't lowercase "Data Analyst" - keep it as is
        data_roles = ["Data Analyst", "Data Scientist", "Data Engineer", "Business Analyst"]
        for role in data_roles:
            if role.lower() in cleaned.lower():
                # Return the properly cased version from the text
                return cleaned
        
        # For other titles, normalize case
        if cleaned.isupper():
            return cleaned.title()
        
        return cleaned
    
    def _is_valid_job_title(self, value: str) -> bool:
        """Check if value is a valid job title (not a skill or tool)"""
        if not value or not isinstance(value, str):
            return False
        
        cleaned = value.strip()
        lowered = cleaned.lower()
        
        if len(cleaned) <= 3:
            return False
        
        # ✅ ACCEPT data/analyst roles
        valid_data_roles = [
            "data analyst", "data scientist", "data engineer", 
            "analyst", "business analyst", "bi analyst",
            "data", "analytics"
        ]
        
        if any(role in lowered for role in valid_data_roles):
            return True
        
        # ✅ ACCEPT developer roles
        dev_roles = [
            "developer", "developpeur", "développeur", "engineer",
            "full stack", "frontend", "backend", "software"
        ]
        
        if any(role in lowered for role in dev_roles):
            return True
        
        # ❌ REJECT skill-like terms
        skill_terms = {
            "python", "java", "javascript", "sql", "excel", "tableau",
            "power bi", "react", "node", "docker", "git"
        }
        
        if lowered in skill_terms:
            return False
        
        return True
    
    def _extract_job_title_from_text(self, raw_text: str) -> str:
        """Extract job title from raw text (only used as fallback)"""
        if not raw_text:
            return ""
        
        lines = [line.strip(" ,|-") for line in raw_text.splitlines() if line.strip()]
        if not lines:
            return ""
        
        # First check for data roles (priority)
        data_keywords = ["data analyst", "data scientist", "data engineer", "business analyst"]
        
        for line in lines[:15]:
            lower = line.lower()
            for keyword in data_keywords:
                if keyword in lower:
                    # Return the original line with proper case
                    return line
        
        # Then check for developer roles
        dev_keywords = ["developpeur", "développeur", "developer", "engineer"]
        
        for line in lines[:15]:
            lower = line.lower()
            if "@" in line or re.search(r"\b\d{8,}\b", line):
                continue
            if len(line) > 80:
                continue
            if any(token in lower for token in ["curriculum vitae", "cv", "resume", "profil"]):
                continue
            if any(token in lower for token in dev_keywords):
                return line
        
        return ""
    
    def _backfill_job_title(self, personal_info: dict, experience_list: list, raw_text: str) -> dict:
        """Fill missing job title ONLY if not already extracted"""
        if not isinstance(personal_info, dict):
            return personal_info
        
        current_title = (personal_info.get("job_title") or "").strip()
        
        # ✅ If we already have a title, TRUST IT (don't override)
        if current_title and len(current_title) > 3:
            # Special handling: if it's a data role, definitely keep it
            data_roles = ["data analyst", "data scientist", "data engineer", "business analyst"]
            if any(role in current_title.lower() for role in data_roles):
                print(f"   ✅ Keeping data role: '{current_title}'")
                personal_info["job_title"] = current_title
                return personal_info
            
            # For developer roles, also keep
            dev_roles = ["developer", "developpeur", "développeur", "engineer"]
            if any(role in current_title.lower() for role in dev_roles):
                print(f"   ✅ Keeping developer role: '{current_title}'")
                personal_info["job_title"] = current_title
                return personal_info
            
            # For any other title with reasonable length
            if len(current_title) > 3:
                print(f"   ✅ Keeping extracted title: '{current_title}'")
                personal_info["job_title"] = current_title
                return personal_info
        
        # ⚠️ Only backfill if no valid title exists
        print(f"   ⚠️ No valid job title extracted, attempting backfill...")
        
        # Try experience titles first
        for exp in experience_list or []:
            if not isinstance(exp, dict):
                continue
            
            title = exp.get("title", "").strip()
            if title and self._is_valid_job_title(title):
                print(f"   📝 Backfilled from experience: '{title}'")
                personal_info["job_title"] = title
                return personal_info
        
        # Try raw text as last resort
        inferred_title = self._extract_job_title_from_text(raw_text)
        if inferred_title:
            print(f"   📝 Backfilled from raw text: '{inferred_title}'")
            personal_info["job_title"] = inferred_title
        
        return personal_info
    
    # ========== LOCATION UTILITIES ==========
    def _extract_location_from_text(self, text: str) -> str:
        """Extract location from raw text"""
        if not text:
            return ""
        
        lines = [line.strip(" ,|-\t") for line in text.splitlines() if line.strip()]
        location_labels = ("location", "lieu", "ville", "address", "adresse")
        
        for line in lines[:20]:
            lower = line.lower()
            if any(label in lower for label in location_labels):
                if ":" in line:
                    return line.split(":", 1)[1].strip()
                if "-" in line:
                    return line.split("-", 1)[1].strip()
                return line.strip()
        
        return ""
    
    def _backfill_profile_location(self, personal_info: dict, raw_text: str) -> dict:
        """Backfill missing location"""
        if not isinstance(personal_info, dict):
            return personal_info
        
        if not (personal_info.get("location") or "").strip():
            inferred_location = self._extract_location_from_text(raw_text)
            if inferred_location:
                personal_info["location"] = inferred_location
        
        return personal_info
    
    # ========== COMBINED EXTRACTION + ANALYSIS ==========
    async def _extract_and_analyze(self, raw_text: str) -> Dict[str, Any]:
        """
        Single LLM call to extract AND analyze resume.
        """
        
        prompt = f"""Extract AND analyze this resume in ONE pass. Return ONLY valid JSON.

IMPORTANT: Extract the EXACT job title as written. If the resume says "Data Analyst", extract "Data Analyst" - NOT "Développeur Python".

REQUIRED OUTPUT STRUCTURE:
{{
    "personal_info": {{
        "job_title": "",  // Extract EXACT title: "Data Analyst", "Data Scientist", "Full-Stack Developer", etc.
        "name": "",
        "email": "",
        "phone": "",
        "location": "",
        "linkedin": "",
        "github": "",
        "portfolio": ""
    }},
    "summary": "",
    "skills": {{
        "technical": [],      // Programming languages, frameworks
        "tools": [],          // Git, Docker, VS Code, etc.
        "databases": [],      // MongoDB, PostgreSQL, etc.
        "ai_ml_skills": [],   // TensorFlow, PyTorch, etc.
        "soft": [],           // Communication, leadership, etc.
        "languages": []       // Spoken languages only
    }},
    "experience": [
        {{
            "title": "",
            "company": "",
            "location": "",
            "start_date": "",
            "end_date": "",
            "responsibilities": []
        }}
    ],
    "education": [
        {{
            "degree": "",
            "institution": "",
            "location": "",
            "graduation_date": ""
        }}
    ],
    "certifications": [],
    "projects": [],
    
    "analysis": {{
        "years_of_experience": 0.0,
        "experience_level": "Junior/Mid/Senior",
        "key_achievements": [],
        "domain_expertise": [],
        "primary_technologies": []
    }}
}}

EXTRACTION RULES:
- job_title: Extract EXACTLY what's on the resume ("Data Analyst", not "Développeur Python")
- Extract ALL technical skills from entire resume
- Keep "Stagiaire"/"Intern" in job titles
- Dates: Look for patterns like "02/2025 – 06/2025"

RESUME TEXT:
{raw_text}

Return ONLY valid JSON, no markdown, no explanations."""

        print(f"   🤖 Running combined extraction + analysis...")
        response = self._query_ollama(prompt)
        result = self._parse_json_safely(response)
        
        if "error" in result:
            raise Exception(f"LLM parsing failed: {result['error']}")
        
        return result
    
    # ========== RUN METHOD ==========
    async def run(self, messages: list) -> Dict[str, Any]:
        """
        Process resume: extract AND analyze in one pass.
        """
        print(f"📄 {self.name}: Starting combined extraction + analysis...")
        
        try:
            last_message = messages[-1]["content"]
            
            if isinstance(last_message, str):
                resume_data = json.loads(last_message)
            else:
                resume_data = last_message
            
            # Extract raw text
            if resume_data.get("file_path"):
                raw_text = extract_text(resume_data["file_path"])
                print(f"   📁 File: {resume_data['file_path']}")
            elif resume_data.get("text"):
                raw_text = resume_data["text"]
            else:
                return {"error": "No valid input. Expecting 'file_path' or 'text'.", "status": "failed"}
            
            if not raw_text or len(raw_text.strip()) < 10:
                return {"error": "Could not extract text from resume", "status": "failed"}
            
            print(f"   📝 Extracted {len(raw_text)} characters")
            
            # ONE LLM call for extraction + analysis
            structured_data = await self._extract_and_analyze(raw_text)
            
            # Post-processing
            structured_data["personal_info"] = self._backfill_profile_location(
                structured_data.get("personal_info", {}),
                raw_text
            )
            
            # Backfill experience dates
            experience_list = structured_data.get("experience", [])
            experience_list = self._backfill_experience_dates(experience_list, raw_text)
            structured_data["experience"] = experience_list
            
            # ✅ IMPORTANT: Backfill job title (this now respects extracted titles)
            structured_data["personal_info"] = self._backfill_job_title(
                structured_data.get("personal_info", {}),
                experience_list,
                raw_text
            )
            
            # Calculate deterministic years
            deterministic_years = self._calculate_years_of_experience(experience_list)
            deterministic_level = self._determine_experience_level(deterministic_years)
            
            if "analysis" not in structured_data:
                structured_data["analysis"] = {}
            
            structured_data["analysis"]["years_of_experience"] = deterministic_years
            structured_data["analysis"]["experience_level"] = deterministic_level
            
            # Print final job title for debugging
            final_title = structured_data.get("personal_info", {}).get("job_title", "Not found")
            print(f"   ✅ Final job title: '{final_title}'")
            print(f"   ✅ Extraction + analysis complete!")
            print(f"   📊 Experience: {deterministic_years} years → {deterministic_level}")
            print(f"   💼 {len(experience_list)} experiences found")
            print(f"   💻 {len(structured_data.get('skills', {}).get('technical', []))} technical skills")
            
            return {
                "raw_text": raw_text,
                "structured_data": structured_data,
                "analysis": structured_data.get("analysis", {}),
                "status": "completed"
            }
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e), "status": "failed"}