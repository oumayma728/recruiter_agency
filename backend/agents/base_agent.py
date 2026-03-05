from typing import Any, Dict
import json
from openai import OpenAI

class BaseAgent:
    def __init__(self, name: str, instructions: str):
        self.name = name
        self.instructions = instructions
        self.ollama_client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """Override this in each agent"""
        raise NotImplementedError("Subclasses must implement this method.")

    def _query_ollama(self, prompt: str) -> str:
        """Ask the ai a question and get the answer"""
        try:
            response = self.ollama_client.chat.completions.create(
                model="llama3.2:latest",
                temperature=0,        # deterministic output for structured data extraction
                max_tokens=2000,
                response_format={"type": "json_object"},  
                messages=[
                    {"role": "system", "content": self.instructions},
                    {"role": "user", "content": prompt}
                ],
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error querying Ollama: {str(e)}")
            raise

    def _parse_json_safely(self, text: str) -> Dict[str, Any]:
        """Parse a JSON string safely with multiple fallback strategies."""
        if not text or not text.strip():
            return {"error": "Empty response from model."}

        # Strategy 1: Strip markdown fences first
        import re
        cleaned = re.sub(r"```(?:json)?\s*", "", text).strip()
        cleaned = re.sub(r"```\s*$", "", cleaned).strip()

        # Strategy 2: Direct parse (model returned clean JSON)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Strategy 3: Extract first {...} block
        try:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1 and end > start:
                json_str = cleaned[start:end + 1]
                return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"   ⚠️ JSON extract failed: {e} | Snippet: {cleaned[start:start+200]}")

        # Strategy 4: Ollama native JSON mode via response_format (add to _query_ollama instead)
        return {"error": f"Failed to parse JSON response. Raw: {text[:200]}"}