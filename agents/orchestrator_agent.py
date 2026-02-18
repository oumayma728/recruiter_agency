from typing import Dict, Any
import json
from .base_agent import BaseAgent
from .extractor_agent import ExtractorAgent
from .analyzer_agent import AnalyzerAgent
from .matcher_agent import MatchAgent
class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Orchestrator",
            instructions="""Coordinate the recruitment workflow and delegate tasks to specialized agents.
            Ensure proper flow of information between extraction, analysis, matching, screening, and recommendation phases.
            Maintain context and aggregate results from each stage."""
        )
        #setup the specialized agents for each phase of the recruitment process
        self._setup_agents()
    def _setup_agents(self):
        """Initialize all agents"""
        self.extractor_agent = ExtractorAgent()
        self.analyzer_agent = AnalyzerAgent()
        self.match_agent = MatchAgent()
    async def run(self,messages:list) -> Dict[str,Any]:
        """Process a single message through the agent"""
        prompt=messages[-1]["content"]
        response=self._query_ollama(prompt)
        return self._parse_json_safely(response)
    async def process_resume(self,resume_input:Dict[str,Any], job_list:list) -> Dict[str,Any]:
        """Main workflow orchestrator for processing a resume through all stages"""
        
        print("🚀 Orchestrator: Starting resume processing workflow...")
        workflow_context = {
            "resume_data": resume_input,
            "status": "initiated"        }

        try:
            #extraction phase
            extracted_data= await self.extractor_agent.run([{"role":"user","content":json.dumps(resume_input)}])
            workflow_context["extracted_data"]=extracted_data
            workflow_context["current_stage"]="analysis"
            if extracted_data.get("extraction_status")!="completed":
                print(f"   ⚠️ Extraction failed: {extracted_data.get('error','Unknown error')}")
                return {
                    "error": extracted_data.get("error","Extraction failed"),
                    "workflow_status": "failed",
                    "current_stage": "extraction"
                }
            #analysis phase
            analysis_results= await self.analyzer_agent.run([{"role":"user","content":extracted_data}])
            workflow_context["analysis_results"]=analysis_results
            workflow_context["current_stage"]="matching"
            if analysis_results.get("analysis_status")!="completed":
                print(f"   ⚠️ Analysis failed: {analysis_results.get('error','Unknown error')}")
                return {
                    "error": analysis_results.get("error","Analysis failed"),
                    "workflow_status": "failed",
                    "current_stage": "analysis"
                }
            #matching phase
            payload={
                "analysis_results": analysis_results,
                "job_list": job_list
            }
            match_results= await self.match_agent.run([{"role":"user","content":json.dumps(payload)}])
            workflow_context["match_results"]=match_results
            workflow_context["current_stage"]="completed"
            if not match_results.get("matched_jobs"):
                print(f"   ⚠️ No matches found: {match_results.get('error','No matches found')}")
                return {
                    "error": match_results.get("error","No matches found"),
                    "workflow_status": "completed",
                    "current_stage": "matching",
                    "match_results": match_results
                }
            return workflow_context
        except Exception as e:
            print(f"Error in workflow: {str(e)}")
            return {
                "error": str(e),
                "workflow_status": "failed",
                "current_stage": workflow_context.get("current_stage", "unknown")
            }