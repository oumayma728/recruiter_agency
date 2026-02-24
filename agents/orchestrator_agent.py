from typing import Dict, Any
import json
from .base_agent import BaseAgent
from .extractor_agent import ExtractorAgent
from .analyzer_agent import AnalyzerAgent
from .matcher_agent import MatchAgent
from .screener_agent import ScreenerAgent       
from .recommender_agent import RecommenderAgent
from .profile_enhacer_agent import ProfileEnhancerAgent
class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Orchestrator",
            instructions="""Coordinate the recruitment workflow and delegate tasks to specialized agents.
            Ensure proper flow of information between extraction, analysis, matching, screening, and recommendation phases.
            Maintain context and aggregate results from each stage."""
        )
        self._setup_agents()

    def _setup_agents(self):
        """Initialize all agents"""
        self.extractor_agent = ExtractorAgent()
        self.analyzer_agent = AnalyzerAgent()
        self.match_agent = MatchAgent()
        self.screener_agent = ScreenerAgent()
        self.recommender_agent = RecommenderAgent()
        self.profile_enhancer_agent = ProfileEnhancerAgent()
    async def run(self, messages: list) -> Dict[str, Any]:
        """Process a single message through the agent"""
        prompt = messages[-1]["content"]
        response = self._query_ollama(prompt)
        return self._parse_json_safely(response)

    async def process_resume(self, resume_input: Dict[str, Any], job_list: list) -> Dict[str, Any]:
        """Main workflow orchestrator for processing a resume through all stages"""

        print("🚀 Orchestrator: Starting resume processing workflow...")
        workflow_context = {
            "resume_data": resume_input,
            "status": "initiated"

        }

        try:
            # extraction phase
            extracted_data = await self.extractor_agent.run([{"role": "user", "content": json.dumps(resume_input)}])
            workflow_context["extracted_data"] = extracted_data

            if extracted_data.get("extraction_status") != "completed":
                print(f"   ⚠️ Extraction failed: {extracted_data.get('error', 'Unknown error')}")
                return {
                    "error": extracted_data.get("error", "Extraction failed"),
                    "workflow_status": "failed",
                    "current_stage": "extraction"
                }

            # analysis phase - ✅ fixed: json.dumps(extracted_data) instead of raw dict
            analysis_results = await self.analyzer_agent.run([{"role": "user", "content": json.dumps(extracted_data)}])
            workflow_context["analysis_results"] = analysis_results
            workflow_context["current_stage"] = "analysis"

            if analysis_results.get("analysis_status") != "completed":
                print(f"   ⚠️ Analysis failed: {analysis_results.get('error', 'Unknown error')}")
                return {
                    "error": analysis_results.get("error", "Analysis failed"),
                    "workflow_status": "failed",
                    "current_stage": "analysis"
                }

            # matching phase - ✅ fixed: key is "skills_analysis" to match what MatchAgent expects
            workflow_context["current_stage"] = "matching"
            payload = {
                "skills_analysis": analysis_results.get("skills_analysis") or {},
                "job_list": job_list or [],
            }
            match_results = await self.match_agent.run([{"role": "user", "content": json.dumps(payload)}])
            workflow_context["match_results"] = match_results

            if not match_results.get("matched_jobs"):
                print(f"   ⚠️ No matches found")
                return {
                    "error": "No matches found",
                    "workflow_status": "completed",
                    "current_stage": "matching",
                    "match_results": match_results
                }
        #screening phase
            workflow_context["current_stage"] = "screening"
            screening_payload = {
                "skills_analysis": analysis_results.get("skills_analysis") or {},
                "matched_jobs": match_results.get("matched_jobs") or []
                }
            screening_results = await self.screener_agent.run([{"role": "user", "content": json.dumps(screening_payload)}])

            workflow_context["screening_results"] = screening_results
            workflow_context["status"] = "completed"
        #recommendation phase
            workflow_context["current_stage"] = "recommendation"
            recommendation_payload = {
                "extraction_results": extracted_data,
                "analysis_results": analysis_results,
                "match_results": match_results,
                "screening_results": screening_results
                }
            recommendation_results = await self.recommender_agent.run([{"role": "user", "content": json.dumps(recommendation_payload)}])
            print(f"   🔍 Recommendation results type: {type(recommendation_results)}")
            print(f"   🔍 Recommendation results keys: {list(recommendation_results.keys())}")
            print(f"   🔍 Has 'recommendation' key: {'recommendation' in recommendation_results}")
            print(f"   🔍 Recommendation value type: {type(recommendation_results.get('recommendation'))}")
            print(f"   🔍 Recommendation keys: {list(recommendation_results.get('recommendation', {}).keys())}")

            workflow_context["recommendation"] = recommendation_results.get("recommendation", {})     
            workflow_context["recommendation_status"] = recommendation_results.get("recommendation_status", "unknown")
            #enhancement phase
            workflow_context["current_stage"] = "profile_enhancement"
            enhancement_payload = {
                "extraction_results": extracted_data,
                "analysis_results": analysis_results,
                "match_results": match_results,
                "screening_results": screening_results,
                "recommendation": workflow_context["recommendation"],
                "recommendation_status": workflow_context["recommendation_status"]
            }
            enhancement_results = await self.profile_enhancer_agent.run([{"role": "user", "content": json.dumps(enhancement_payload)}])
            workflow_context["enhancement_results"] = enhancement_results
            return workflow_context
        except Exception as e:
            print(f"Error in workflow: {str(e)}")
            return {
                "error": str(e),
                "workflow_status": "failed",
                "current_stage": workflow_context.get("current_stage", "unknown")
            }