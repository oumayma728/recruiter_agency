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
                temperature=0,        # ✅ only once
                max_tokens=2000,
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
        """Parse a JSON string safely, returning an empty dictionary if parsing fails."""
        try:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                json_str = text[start:end+1]
                return json.loads(json_str)
            return {"error": "No JSON found in the response."}
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON response."}  