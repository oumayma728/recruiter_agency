from typing import Any, Dict #define the types for the input and output of the agent
import json
from openai import OpenAI #import the OpenAI client to interact with the Ollama API
class BaseAgent:
    """
    Base class for all Ai agents.
    Each agent will inherit this to get basic Ai capabilities.
    """
    #Constructor to initialize the agent with a name and instructions, and set up the Ollama client
    def __init__(self,name:str,instructions:str):
        self.name = name
        self.instructions = instructions
        self.ollama_client=OpenAI(
            base_url="http://localhost:11434/v1",  # Your computer
            api_key="ollama",  # Dummy key 
        )
        #checks if the model is available
    async def run(self,messages:list) ->Dict[str,Any]:
        """Override this in each agent"""
        raise NotImplementedError("Subclasses must implement this method to define how the agent processes messages.")
    # start with _ to indicate it's a private method, and it will be used internally by the agent to query the Ollama API with a given prompt and return the response as a string.
    #
    def _query_ollama(self, prompt:str) -> str:
        """Ask the ai a question and get the answer"""
        try:
            response= self.ollama_client.chat.completions.create(
            model="llama3.2:latest",

            #role is either system, user, or assistant. System is for instructions, user is for questions, and assistant is for the ai's responses.
            messages=[
                {"role":"system","content":self.instructions},
                {"role":"user","content":prompt}
            ],
            #temperature controls the randomness of the output, with higher values producing more creative responses and lower values producing more deterministic responses.
            temperature=0.7,
            max_tokens=2000, #max tokens is the maximum length of the response in tokens, which are chunks of words
            )
            return response.choices[0].message.content.strip() #return the content of the first choice, which is the ai's response, and strip any leading or trailing whitespace
        except Exception as e:
            print(f"Error querying Ollama: {str(e)}")
            raise
    def _parse_json_safely(self,text:str) -> Dict[str,Any]:#return dictionary from json string, but if it's not valid json, return an empty dictionary
        """Parse a JSON string safely, returning an empty dictionary if parsing fails."""
        try:
            start=text.find("{") #search for the first occurrence of '{' to find the start of the JSON object
            end = text.rfind("}") #search for the last occurrence of '}' to find the end of the JSON object
            if start != -1 and end !=-1:
                json_str=text[start:end+1] #extract the substring that contains the JSON object
                return json.loads(json_str)
            return {"error ":"No JSON found in the response."} #if no JSON object is found, return an error message in a dictionary
        except json.JSONDecodeError:
            return