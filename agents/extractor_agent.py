from typing import Dict, Any
import json
from pdfminer.high_level import extract_text
from .base_agent import BaseAgent

class ExtractorAgent(BaseAgent):
    def __init__(self):
        name="ExtractorAgent"
        instructions=("""You are a resume extraction expert.
Extract structured information from resumes and return ONLY valid JSON.

Required JSON format:
{
"personal_info": {
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
    "gpa": ""
    }
],
    "certifications": [],
    "projects": []
}

Return ONLY the JSON object, no explanations or markdown."""
        )
async def run(self, messages:list) -> Dict[str,Any]:
    """
        Process resume and extract structured information.
        
        Expected message format:
        {"file_path": "path/to/resume.pdf"} OR {"text": "resume text"}
    """
    print(f"📄 {self.name}: Starting extraction...")
    try:
        last_message = messages[-1]["content"]
        #convert input into a dictionary if it's a string
        if isinstance(last_message,str):
            resume_data=json.loads(last_message)
        else:
            resume_data=last_message
        if resume_data.get("file_path"):
            raw_text=extract_text(resume_data["file_path"])
        elif resume_data.get("text"):
            raw_text=resume_data["text"]
        else:
            return {"error":"No valid input provided. Expecting 'file_path' or 'text'."}
        if not raw_text or len(raw_text.strip())<10:
            return {
                "error": "Could not extract text from resume",
                "extraction_status": "failed"
                }
        #build the ai prompt 
        prompt = f"""Extract information from this resume and return ONLY valid JSON:
        {raw_text}
        Remember: Return ONLY the JSON object, no other text
        """ 
        #sends prompt to ollama
        ai_response=self._query_ollama(prompt)
        #parse the ai response
        structured_data=self._parse_json_safely(ai_response)
        if "error" in structured_data:
            return {
                "error": "AI response did not contain valid JSON",
                "ai_response": ai_response,
                "extraction_status": "failed"
            }
        return {
            "raw_text": raw_text,
            "structured_data": structured_data,
            "extraction_status": "completed"
}   
    except Exception as e:
        return {
    "error": str(e),
    "extraction_status": "failed"
}
