from typing import Dict, Any
import json
import re
from datetime import datetime
from pdfminer.high_level import extract_text
from .base_agent import BaseAgent

class ExtractorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Extractor",
            instructions=("""You are a resume extraction expert.
Extract structured information from resumes and return ONLY valid JSON.

Required JSON format:
{
"personal_info": {
    "job_title": "",
    "name": "",
    "email": "",
    "phone": "",
    "location": "",
    "linkedin": "",
    "github": "",
    "portfolio": ""
},
"summary": "",
    "skills": {
        "technical": [],
        "soft": [],
        "languages": []
},
"experience": [
    {
    "title": "",
    "company": "",
    "location": "",
    "start_date": "",
    "end_date": "",
    "responsibilities": []
    }
],
"education": [
    {
    "degree": "",
    "institution": "",
    "location": "",
    "graduation_date": "",
    }
],
    "certifications": [],
    "projects": []
}

Return ONLY the JSON object, no explanations or markdown.""")
        )
    
    def _calculate_years_of_experience(self, experience_list: list) -> float:
        """
        Calcule le nombre total d'années d'expérience à partir de la liste des expériences.
        Un stage de 6 mois = 0.5 an
        """
        total_months = 0
        
        for exp in experience_list:
            start = exp.get("start_date", "")
            end = exp.get("end_date", "")
            
            if not start or not end:
                continue
            
            # Si "Present", on prend la date actuelle
            if end.lower() in ["present", "pré sent", "now"]:
                end = datetime.now().strftime("%m/%Y")
            
            # Essayer différents formats de date
            try:
                # Format "MM/YYYY"
                if "/" in start:
                    start_month, start_year = map(int, start.split("/")[:2])
                    end_month, end_year = map(int, end.split("/")[:2])
                # Format "Month YYYY"
                else:
                    months = {"jan":1, "feb":2, "mar":3, "apr":4, "may":5, "jun":6,
                             "jul":7, "aug":8, "sep":9, "oct":10, "nov":11, "dec":12}
                    start_parts = start.lower().split()
                    end_parts = end.lower().split()
                    start_month = months.get(start_parts[0][:3], 1)
                    start_year = int(start_parts[1])
                    end_month = months.get(end_parts[0][:3], 1)
                    end_year = int(end_parts[1])
                
                # Calculer les mois d'expérience
                months_diff = (end_year - start_year) * 12 + (end_month - start_month)
                
                # Vérifier si c'est un stage (moins de 12 mois)
                title = exp.get("title", "").lower()
                if "stagiaire" in title or "intern" in title:
                    months_diff = min(months_diff, 6)  # Max 6 mois pour un stage
                
                total_months += max(0, months_diff)
                
            except Exception as e:
                print(f"   ⚠️ Erreur parsing date: {start} - {end} -> {e}")
                continue
        
        years = total_months / 12
        return round(years, 1)

    def _normalize_date_value(self, value: str) -> str:
        """Normalize common date values to a consistent CV-friendly format."""
        if not value or not isinstance(value, str):
            return ""

        cleaned = value.strip()
        lower = cleaned.lower()

        if lower in ["present", "now", "current", "ongoing", "today"]:
            return "Present"

        # Keep MM/YYYY as-is.
        if re.match(r"^\d{1,2}/\d{4}$", cleaned):
            month, year = cleaned.split("/")
            return f"{int(month):02d}/{year}"

        # Convert YYYY-MM or YYYY/MM to MM/YYYY.
        match = re.match(r"^(\d{4})[-/](\d{1,2})$", cleaned)
        if match:
            year, month = match.groups()
            return f"{int(month):02d}/{year}"

        return cleaned

    def _extract_date_ranges_from_text(self, text: str) -> list:
        """Extract date ranges from raw CV text in common resume formats."""
        if not text:
            return []

        normalized_text = text.replace("\u2013", "-").replace("\u2014", "-")

        month_names = (
            "jan|january|janv|janvier|feb|february|fev|fevrier|mar|march|mars|apr|april|avr|avril|"
            "may|mai|jun|june|juin|jul|july|juil|juillet|aug|august|aou|aout|sep|sept|september|"
            "oct|october|nov|november|dec|december|decembre"
        )

        date_patterns = [
            # MM/YYYY - MM/YYYY or MM/YYYY - Present
            rf"\b(\d{{1,2}}/\d{{4}})\s*[-–—]\s*(\d{{1,2}}/\d{{4}}|present|now|current|ongoing|today)\b",
            # Month YYYY - Month YYYY / Present
            rf"\b(?:{month_names})\s+\d{{4}}\s*[-–—]\s*(?:{month_names})\s+\d{{4}}\b",
            rf"\b(?:{month_names})\s+\d{{4}}\s*[-–—]\s*(?:present|now|current|ongoing|today)\b",
            # Year - Year
            r"\b(\d{4})\s*[-–—]\s*(\d{4}|present|now|current|ongoing|today)\b",
        ]

        ranges = []
        for pattern in date_patterns:
            for match in re.finditer(pattern, normalized_text, flags=re.IGNORECASE):
                raw_range = match.group(0)
                parts = re.split(r"\s*[-–—]\s*", raw_range)
                if len(parts) != 2:
                    continue

                start = self._normalize_date_value(parts[0])
                end = self._normalize_date_value(parts[1])

                # Skip incomplete captures like year-only ranges; they are too noisy.
                if re.fullmatch(r"\d{4}", start) or re.fullmatch(r"\d{4}", end):
                    continue

                ranges.append((start, end))

        # Keep order, remove exact duplicates.
        unique_ranges = []
        seen = set()
        for start, end in ranges:
            key = (start, end)
            if key not in seen:
                seen.add(key)
                unique_ranges.append({"start_date": start, "end_date": end})

        return unique_ranges

    def _backfill_experience_dates(self, experience_list: list, raw_text: str) -> list:
        """Fill missing experience dates from the raw CV text when the model omits them."""
        if not isinstance(experience_list, list):
            return experience_list

        date_ranges = self._extract_date_ranges_from_text(raw_text)
        if not date_ranges:
            return experience_list

        filled = []
        range_index = 0
        for exp in experience_list:
            if not isinstance(exp, dict):
                filled.append(exp)
                continue

            start = (exp.get("start_date") or "").strip()
            end = (exp.get("end_date") or "").strip()

            if (not start or not end) and range_index < len(date_ranges):
                inferred = date_ranges[range_index]
                range_index += 1

                if not start:
                    exp["start_date"] = inferred["start_date"]
                if not end:
                    exp["end_date"] = inferred["end_date"]

            filled.append(exp)

        return filled
    
    def _determine_experience_level(self, years: float) -> str:
        """Détermine le niveau d'expérience (Junior/Mid/Senior)"""
        if years < 2:
            return "Junior"
        elif years <= 5:
            return "Mid"
        else:
            return "Senior"
    
    async def run(self, messages: list) -> Dict[str, Any]:
        """
        Process resume and extract structured information.
        
        Expected message format:
        {"file_path": "path/to/resume.pdf"} OR {"text": "resume text"}
        """
        print(f"📄 {self.name}: Starting extraction...")
        
        try:
            last_message = messages[-1]["content"]
            
            # Convert input into a dictionary if it's a string
            if isinstance(last_message, str):
                resume_data = json.loads(last_message)
            else:
                resume_data = last_message
                
            # Extract raw text from PDF or direct text
            if resume_data.get("file_path"):
                raw_text = extract_text(resume_data["file_path"])
                print(f"   📁 Fichier: {resume_data['file_path']}")
            elif resume_data.get("text"):
                raw_text = resume_data["text"]
            else:
                return {"error": "No valid input provided. Expecting 'file_path' or 'text'."}
                
            if not raw_text or len(raw_text.strip()) < 10:
                return {
                    "error": "Could not extract text from resume",
                    "extraction_status": "failed"
                }
            
            print(f"   📝 Texte extrait: {len(raw_text)} caractères")
            
            # Build the AI prompt with strict rules
            prompt = f"""Extract information from this resume and return ONLY valid JSON.

📋 STRICT EXTRACTION RULES:

1. 🏢 **EXPERIENCE**
   - "title": Le titre EXACT du poste (ex: "Stagiaire Développeuse Full-Stack")
   - Garde le mot "Stagiaire" si présent → c'est important
   - "start_date" et "end_date": Cherche des patterns comme "02/2025 – 06/2025"
   - Les dates sont souvent listées SÉPARÉMENT du titre, associe-les par ordre d'apparition

2. 🎓 **ÉDUCATION**
   - "degree": Le nom EXACT du diplôme (ex: "Cycle d'Ingénieur en Informatique")
   - "institution": Le nom de l'école

3. 👤 **INFORMATIONS PERSONNELLES**
   - "job_title": La ligne sous le nom (ex: "Développeuse Full-Stack | Web, Mobile & IA")
   - "location": La ville extraite (ex: "Bizerte", "Tunis")
   - "name": Le nom complet
   - "email": Format xxx@xxx.xxx
   - "phone": Numéro de téléphone

4. 💻 **COMPÉTENCES**
   - "technical": Langages et frameworks (Python, React, Node.js)
   - "tools": Outils (Git, Docker, VS Code)
   - "databases": Bases de données (MongoDB, PostgreSQL)
   - "languages": Langues PARLÉES (Français, Anglais, Arabe) → PAS des langages de programmation !

5. 📊 **PROJETS**
   - Extrais les projets personnels et académiques
   - Inclus les technologies utilisées

📄 RESUME:
{raw_text}

🎯 Return ONLY the JSON object with this exact structure. NO MARKDOWN, NO EXPLANATIONS.
"""
            
            # Send prompt to Ollama
            print(f"   🤖 Envoi à Ollama...")
            ai_response = self._query_ollama(prompt)
            
            # Parse the AI response
            structured_data = self._parse_json_safely(ai_response)
            
            if "error" in structured_data:
                return {
                    "error": "AI response did not contain valid JSON",
                    "ai_response": ai_response[:500],  # Garder les 500 premiers caractères pour debug
                    "extraction_status": "failed"
                }
            
            # 🔧 POST-TRAITEMENT: Calculer les années d'expérience
            experience_list = structured_data.get("experience", [])
            experience_list = self._backfill_experience_dates(experience_list, raw_text)
            structured_data["experience"] = experience_list
            years = self._calculate_years_of_experience(experience_list)
            level = self._determine_experience_level(years)
            
            # Ajouter les années d'expérience calculées
            structured_data["years_of_experience"] = years
            structured_data["experience_level"] = level
            
            print(f"   ✅ Extraction terminée!")
            print(f"   📊 Années d'expérience calculées: {years} → {level}")
            print(f"   💼 {len(experience_list)} expériences trouvées")
            print(f"   💻 {len(structured_data.get('skills', {}).get('technical', []))} compétences techniques")
            
            return {
                "raw_text": raw_text,
                "structured_data": structured_data,
                "extraction_status": "completed"
            }
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "extraction_status": "failed"
            }