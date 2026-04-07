from typing import Dict, Any, List
import json
from .base_agent import BaseAgent
from .ResumeAnalyzerAgent import ResumeAnalyzerAgent  # NEW: merged extractor+analyzer
from .profile_enhacer_agent import ProfileEnhancerAgent  # KEPT: conditional
from .RankingAgent import RankingAgent  # NEW: merged matcher+screener+recommender

class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Orchestrator",
            instructions="""Coordinate recruitment workflow with optimized agent architecture.
            Uses 3 specialized agents instead of 7 for 70% faster processing."""
        )
        self._setup_agents()

    def _setup_agents(self):
        """Initialize optimized agents (3 instead of 7)"""
        self.resume_analyzer = ResumeAnalyzerAgent()  # Extractor + Analyzer
        self.profile_enhancer = ProfileEnhancerAgent()  # Kept separate (conditional)
        self.ranking_agent = RankingAgent()  # Matcher + Screener + Recommender

    async def run(self, messages: list) -> Dict[str, Any]:
        """Process a single message through the agent"""
        prompt = messages[-1]["content"]
        response = self._query_ollama(prompt)
        return self._parse_json_safely(response)

    async def process_resume(self, resume_input: Dict[str, Any], job_list: List[Dict]) -> Dict[str, Any]:
        """
        Main workflow with optimized 3-agent pipeline.
        
        Args:
            resume_input: {"file_path": "path/to/resume.pdf"} or {"text": "resume text"}
            job_list: List of job dicts from scraper
        
        Returns:
            Complete workflow results with recommendations
        """
        print("🚀 Orchestrator: Starting workflow ...")
        
        workflow_context = {
            "resume_data": resume_input,
            "status": "initiated",
            "job_count": len(job_list) if job_list else 0
        }

        try:
            # ========== STEP 1: Analyze Resume (Extraction + Analysis in ONE) ==========
            print("\n📝 STEP 1: Resume Analysis ")
            print("-" * 50)
            analysis_result = await self.resume_analyzer.run([
                {"role": "user", "content": json.dumps(resume_input)}
            ])
            
            if analysis_result.get("status") != "completed":
                print(f"   ❌ Resume analysis failed: {analysis_result.get('error', 'Unknown error')}")
                return {
                    "error": analysis_result.get("error", "Resume analysis failed"),
                    "workflow_status": "failed",
                    "current_stage": "resume_analysis"
                }
            
            candidate_profile = analysis_result.get("structured_data", {})
            candidate_analysis = analysis_result.get("analysis", {})
            
            print(f"   ✅ Candidate: {candidate_profile.get('personal_info', {}).get('name', 'Unknown')}")
            print(f"   ✅ Experience: {candidate_analysis.get('years_of_experience', 0)} years ({candidate_analysis.get('experience_level', 'Unknown')})")
            print(f"   ✅ Skills: {len(candidate_profile.get('skills', {}).get('technical', []))} technical skills")
            
            workflow_context["candidate_profile"] = candidate_profile
            workflow_context["candidate_analysis"] = candidate_analysis
            workflow_context["current_stage"] = "resume_analysis"

            # ========== STEP 2: Optional Profile Enhancement ==========
            # Only enhance if candidate is promising (saves 2-3 seconds for weak candidates)
            workflow_context["current_stage"] = "profile_enhancement"
            
            should_enhance = self._should_enhance_profile(candidate_analysis)
            
            if should_enhance:
                print("\n💡 STEP 2: Profile Enhancement")
                print("-" * 50)
                
                skills_data = candidate_profile.get("skills", {})
                all_skills = (
                    skills_data.get("technical", []) +
                    skills_data.get("tools", []) +
                    skills_data.get("databases", [])
                )
                
                enhancement_payload = {
                    "skills": all_skills,
                    "experience": candidate_analysis.get("years_of_experience", 0),
                    "experience_level": candidate_analysis.get("experience_level", "Junior"),
                    "achievements": candidate_analysis.get("key_achievements", []),
                    "domain": candidate_analysis.get("domain_expertise", [])
                }
                
                enhancement_result = await self.profile_enhancer.run([
                    {"role": "user", "content": json.dumps(enhancement_payload)}
                ])
                
                if enhancement_result.get("enhancement_status") == "success":
                    workflow_context["enhancement_results"] = enhancement_result
                    print(f"   ✅ Generated {len(enhancement_result.get('recommendations', []))} recommendations")
                else:
                    print(f"   ⚠️ Enhancement skipped or failed")
                    workflow_context["enhancement_results"] = {"recommendations": []}
            else:
                print("\n💡 STEP 2: Profile Enhancement (SKIPPED - candidate needs improvement first)")
                workflow_context["enhancement_results"] = {"recommendations": [], "skipped": True}

            # ========== STEP 3: Ranking (Matching + Screening + Recommendation in ONE) ==========
            print("\n🎯 STEP 3: Job Ranking & Recommendation")
            print("-" * 50)
            
            if not job_list:
                print("   ⚠️ No jobs provided for matching")
                return {
                    "error": "No jobs to match against",
                    "workflow_status": "failed",
                    "current_stage": "ranking",
                    **workflow_context
                }
            
            ranking_payload = {
                "candidate_profile": {
                    "skills": candidate_profile.get("skills", {}),
                    "analysis": candidate_analysis,
                    "personal_info": candidate_profile.get("personal_info", {})
                },
                "job_list": job_list
            }
            
            ranking_result = await self.ranking_agent.run([
                {"role": "user", "content": json.dumps(ranking_payload)}
            ])
            
            if ranking_result.get("status") != "completed":
                print(f"   ❌ Ranking failed: {ranking_result.get('error', 'Unknown error')}")
                return {
                    "error": ranking_result.get("error", "Ranking failed"),
                    "workflow_status": "failed",
                    "current_stage": "ranking",
                    **workflow_context
                }
            
            workflow_context["ranking_results"] = ranking_result
            workflow_context["current_stage"] = "ranking"

            # ========== BUILD FINAL RESPONSE ==========
            print("\n📊 Building final recommendation...")
            print("-" * 50)
            
            # Extract key data
            top_recommendations = ranking_result.get("top_recommendations", [])
            screening_summary = ranking_result.get("screening_summary", {})
            candidate_summary = ranking_result.get("candidate_summary", {})
            
            # Build final recommendation object (compatible with frontend)
            final_recommendation = self._build_final_recommendation(
                candidate_profile=candidate_profile,
                candidate_analysis=candidate_analysis,
                ranking_result=ranking_result,
                enhancement_result=workflow_context.get("enhancement_results", {})
            )
            
            workflow_context["recommendation"] = final_recommendation
            workflow_context["workflow_status"] = "completed"
            workflow_context["current_stage"] = "complete"
            
            # Print summary
            print("\n" + "="*50)
            print("✅ WORKFLOW COMPLETE")
            print("="*50)
            print(f"📊 Screening: {screening_summary.get('passed_screening', 0)}/{screening_summary.get('total_jobs', 0)} jobs passed")
            print(f"🎯 Top matches: {len(top_recommendations)} jobs")
            print(f"💡 Recommendation: {final_recommendation.get('hiring_recommendation', 'N/A')}")
            print(f"📈 Confidence: {final_recommendation.get('confidence_level', 'N/A')}")
            
            return workflow_context
            
        except Exception as e:
            print(f"\n❌ Workflow error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "workflow_status": "failed",
                "current_stage": workflow_context.get("current_stage", "unknown")
            }

    def _should_enhance_profile(self, candidate_analysis: Dict[str, Any]) -> bool:
        """
        Determine if profile enhancement is worth the LLM call.
        Only enhance if candidate has basic qualifications.
        """
        years_exp = candidate_analysis.get("years_of_experience", 0)
        skills_count = len(candidate_analysis.get("primary_technologies", []))
        
        # Skip enhancement for very weak candidates
        if years_exp < 1 and skills_count < 3:
            print(f"   ⏭️ Skipping enhancement: insufficient experience ({years_exp}y) or skills ({skills_count})")
            return False
        
        # Skip if already strong
        if years_exp >= 5 and skills_count >= 10:
            print(f"   ⏭️ Skipping enhancement: profile already strong")
            return False
        
        print(f"   ✅ Will enhance: {years_exp}y exp, {skills_count} skills")
        return True

    def _build_final_recommendation(self, 
                                    candidate_profile: Dict,
                                    candidate_analysis: Dict,
                                    ranking_result: Dict,
                                    enhancement_result: Dict) -> Dict[str, Any]:
        """
        Build final recommendation object compatible with frontend expectations.
        """
        top_recommendations = ranking_result.get("top_recommendations", [])
        screening_summary = ranking_result.get("screening_summary", {})
        candidate_summary = ranking_result.get("candidate_summary", {})
        
        # Determine hiring recommendation
        if top_recommendations:
            top_score = int(top_recommendations[0].get("match_score", "0%").rstrip("%"))
            if top_score >= 70:
                hiring_recommendation = "PROCEED"
                confidence_level = "HIGH"
            elif top_score >= 50:
                hiring_recommendation = "CONSIDER"
                confidence_level = "MEDIUM"
            else:
                hiring_recommendation = "PASS"
                confidence_level = "LOW"
        else:
            hiring_recommendation = "PASS"
            confidence_level = "LOW"
        
        # Overall assessment
        if top_recommendations:
            best_job = top_recommendations[0]
            overall_assessment = (
                f"Candidate matches {best_job.get('title')} at {best_job.get('company')} "
                f"with {best_job.get('match_score')} score. "
                f"{len(enhancement_result.get('recommendations', []))} improvements suggested."
            )
        else:
            overall_assessment = "No strong matches found. Consider expanding search criteria or skill development."
        
        # Strengths (from analysis)
        strengths = candidate_analysis.get("key_achievements", [])[:3]
        if not strengths:
            primary_skills = candidate_summary.get("primary_skills", [])[:3]
            strengths = [f"Proficient in {skill}" for skill in primary_skills]
        
        if not strengths:
            strengths = ["Technical skills identified", "Profile successfully processed"]
        
        # Concerns
        concerns = []
        if not top_recommendations:
            concerns.append("No strong job matches found")
        elif top_recommendations:
            top_score = int(top_recommendations[0].get("match_score", "0%").rstrip("%"))
            if top_score < 60:
                concerns.append(f"Match score below 60% - skill gap may exist")
        
        if candidate_analysis.get("years_of_experience", 0) < 2:
            concerns.append("Limited professional experience")
        
        # Next steps
        next_steps = []
        if top_recommendations and hiring_recommendation in ["PROCEED", "CONSIDER"]:
            next_steps.append(f"Schedule technical interview for {top_recommendations[0].get('title')}")
            next_steps.append("Request portfolio review or code sample")
        else:
            next_steps.append("Expand job search criteria")
            next_steps.append("Consider additional skill development")
        
        next_steps.append("Document candidate in ATS for future opportunities")
        
        # Interview questions (from ranking agent or default)
        if top_recommendations and top_recommendations[0].get("interview_questions"):
            interview_questions = top_recommendations[0].get("interview_questions", [])
        else:
            interview_questions = [
                "What are your strongest technical skills?",
                "Describe a challenging project you've worked on",
                "How do you approach learning new technologies?"
            ]
        
        return {
            "hiring_recommendation": hiring_recommendation,
            "overall_assessment": overall_assessment,
            "confidence_level": confidence_level,
            "strengths": strengths[:5],
            "concerns": concerns[:3],
            "next_steps": next_steps[:4],
            "interview_questions": interview_questions[:3],
            "top_matches": top_recommendations[:3],
            "screening_summary": screening_summary
        }