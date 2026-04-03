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
            extracted_response = await self.extractor_agent.run([{"role": "user", "content": json.dumps(resume_input)}])
            if extracted_response.get("extraction_status") != "completed":
                print(f"   ⚠️ Extraction failed: {extracted_response.get('error', 'Unknown error')}")
                return {
                    "error": extracted_response.get("error", "Extraction failed"),
                    "workflow_status": "failed",
                    "current_stage": "extraction"
                }

            extracted_data = extracted_response.get("structured_data", {})
            print("📄 Extracted Data:", json.dumps(extracted_data, indent=2))
            workflow_context["extracted_data"] = extracted_data

            # analysis phase
            analysis_results = await self.analyzer_agent.run([{"role": "user", "content": json.dumps(extracted_response)}])
            workflow_context["analysis_results"] = analysis_results
            workflow_context["current_stage"] = "analysis"

            if analysis_results.get("analysis_status") != "completed":
                print(f"   ⚠️ Analysis failed: {analysis_results.get('error', 'Unknown error')}")
                return {
                    "error": analysis_results.get("error", "Analysis failed"),
                    "workflow_status": "failed",
                    "current_stage": "analysis"
                }

            # matching phase
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
            
            # screening phase
            workflow_context["current_stage"] = "screening"
            screening_payload = {
                "skills_analysis": analysis_results.get("skills_analysis") or {},
                "matched_jobs": match_results.get("matched_jobs") or []
            }
            screening_results = await self.screener_agent.run([{"role": "user", "content": json.dumps(screening_payload)}])
            workflow_context["screening_results"] = screening_results
            workflow_context["status"] = "completed"
            
            # recommendation phase
            workflow_context["current_stage"] = "recommendation"
            recommendation_payload = {
                "extraction_results": extracted_data,
                "analysis_results": analysis_results,
                "match_results": match_results,
                "screening_results": screening_results
            }
            recommendation_results = await self.recommender_agent.run([{"role": "user", "content": json.dumps(recommendation_payload)}])
            
            if recommendation_results is None:
                print(f"   ⚠️ Recommendation failed: No response from RecommenderAgent")
                return {
                    "error": "Recommendation failed",
                    "workflow_status": "failed",
                    "current_stage": "recommendation"
                }
            workflow_context["recommendation_results"] = recommendation_results
            
            # enhancement phase
            workflow_context["current_stage"] = "profile_enhancement"

            skills_analysis = analysis_results.get("skills_analysis", {})

            all_skills = (
                skills_analysis.get("technical_skills", []) +
                skills_analysis.get("tools", []) +
                skills_analysis.get("databases", []) +
                skills_analysis.get("ai_ml_skills", [])
            )

            enhancement_payload = {
                "skills": all_skills,
                "experience": skills_analysis.get("years_of_experience", 0),
                "experience_level": skills_analysis.get("experience_level", "Junior"),
                "achievements": skills_analysis.get("key_achievements", []),
                "domain": skills_analysis.get("domain_expertise", [])
            }

            print(f"   📊 Sending to enhancer: {len(enhancement_payload['skills'])} skills")
            print(f"   📊 Skills sample: {enhancement_payload['skills'][:5]}")

            enhancement_results = await self.profile_enhancer_agent.run([{"role": "user", "content": json.dumps(enhancement_payload)}])
            
            if enhancement_results is None:
                print(f"   ⚠️ Profile enhancement failed: No response from ProfileEnhancerAgent")
                return {
                    "error": "Profile enhancement failed",
                    "workflow_status": "failed",
                    "current_stage": "profile_enhancement"
                }
            workflow_context["enhancement_results"] = enhancement_results

            # ========== BUILD FRONTEND RECOMMENDATION OBJECT ==========
            print(f"🔍 [DEBUG] Building recommendation object...")
        
            matched_jobs = match_results.get("matched_jobs", [])
            print(f"🔍 [DEBUG] matched_jobs: {matched_jobs}")
            
            candidate_skills = skills_analysis.get("technical_skills", [])
            print(f"🔍 [DEBUG] candidate_skills count: {len(candidate_skills)}")
            
            enhancement_recs = enhancement_results.get("recommendations", [])
            print(f"🔍 [DEBUG] enhancement_recs count: {len(enhancement_recs)}")
            top_match_score = 0
            if matched_jobs and len(matched_jobs) > 0:
                score_str = matched_jobs[0].get("match_score", "0%")
                top_match_score = int(score_str.rstrip("%"))
            
            # Hiring recommendation
            if top_match_score >= 70:
                hiring_recommendation = "PROCEED"
            elif top_match_score >= 50:
                hiring_recommendation = "CONSIDER"
            else:
                hiring_recommendation = "PASS"
            
            # Confidence level
            if top_match_score >= 70:
                confidence_level = "HIGH"
            elif top_match_score >= 50:
                confidence_level = "MEDIUM"
            else:
                confidence_level = "LOW"
            
            # Overall assessment
            if matched_jobs and top_match_score >= 50:
                overall_assessment = f"Candidate matches {matched_jobs[0].get('title')} at {matched_jobs[0].get('company')} with {top_match_score}% score. {len(enhancement_recs)} improvements suggested."
            elif matched_jobs:
                overall_assessment = f"Candidate has {top_match_score}% match with top job. Consider skill development."
            else:
                overall_assessment = "No strong matches found. Consider expanding search criteria."
            
            # Strengths
            strengths = [f"Strong proficiency in {skill}" for skill in candidate_skills[:5]]
            if not strengths:
                strengths = ["Technical skills detected"]
            
            # Concerns
            concerns = []
            if not matched_jobs:
                concerns.append("No direct job matches found")
            elif top_match_score < 60:
                concerns.append(f"Match score below 60% - skill gap may exist")
            
            # Next steps
            next_steps = []
            if matched_jobs and top_match_score >= 50:
                next_steps.append(f"Schedule technical interview for {matched_jobs[0].get('title')} position")
                next_steps.append("Request portfolio review or code sample")
            else:
                next_steps.append("Expand job search criteria")
                next_steps.append("Consider additional skill development")
            next_steps.append("Follow up with candidate for additional information")
            
            # Interview questions
            interview_questions = [
                "What are your strongest technical skills?",
                "Describe a challenging project you worked on",
                "How do you approach learning new technologies?"
            ]
            
            # Create the recommendation object
            workflow_context["recommendation"] = {
                "hiring_recommendation": hiring_recommendation,
                "overall_assessment": overall_assessment,
                "confidence_level": confidence_level,
                "strengths": strengths,
                "concerns": concerns,
                "next_steps": next_steps,
                "interview_questions": interview_questions
            }
            
            # FINAL RETURN
            workflow_context["workflow_status"] = "completed"
            workflow_context["current_stage"] = "complete"
            
            return workflow_context
            
        except Exception as e:
            print(f"Error in workflow: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "workflow_status": "failed",
                "current_stage": workflow_context.get("current_stage", "unknown")
            }