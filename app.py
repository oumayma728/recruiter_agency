import streamlit as st
import tempfile
import asyncio
from agents.orchestrator_agent import OrchestratorAgent
from db.database import JobDatabase

def save_uploaded_file(uploaded_file):
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        return tmp_file.name

def load_job_database():
    db = JobDatabase()
    return db.get_all_jobs()

async def process_resume(file_path: str, job_list: list) -> dict:
    try:
        orchestrator_agent = OrchestratorAgent()
        resume_data = {
            "file_path": file_path,
            "job_list": job_list
        }
        result = await orchestrator_agent.process_resume(resume_data, job_list)
        return result
    except Exception as e:
        return {"error": str(e), "workflow_status": "failed"}

def main():
    st.set_page_config(page_title="AI Recruiter Agency", page_icon="🤖", layout="centered")
    st.title("🤖 AI Recruiter Agency")
    st.write("Upload a resume to find the best job matches based on skills and experience.")

    job_list = load_job_database()
    if not job_list:
        st.error("No job postings found in the database. Please add some jobs before using the matching feature.")
        return

    st.info(f"Loaded {len(job_list)} job postings from the database.")
    uploaded_file = st.file_uploader("Upload your CV", type=["pdf"])

    if st.button("Find Matches"):
        if not uploaded_file:
            st.warning("Please upload a resume before finding matches.")
        else:
            file_path = save_uploaded_file(uploaded_file)
            st.success("Resume uploaded successfully! Processing...")

            with st.spinner("Analyzing resume and finding matches..."):
                results = asyncio.run(process_resume(file_path, job_list))

            if results.get("error"):
                st.error(f"Error processing resume: {results['error']}")
            else:
                st.success("Resume processed successfully! Here are the results:")
                tab1, tab2, tab3 = st.tabs(["Extracted Data", "Analysis Results", "Matched Jobs"])

                with tab1:
                    st.subheader("Candidate Analysis - Extracted Data")

                    extracted = results.get("extracted_data", {})
                    structured = extracted.get("structured_data", {})
                    personal_info = structured.get("personal_info", {})

                    if personal_info:
                        st.write("### 👤 Personal Info")
                        st.write(f"**Name:** {personal_info.get('name', 'N/A')}")
                        st.write(f"**Email:** {personal_info.get('email', 'N/A')}")
                        st.write(f"**Phone:** {personal_info.get('phone', 'N/A')}")
                        st.write(f"**Location:** {personal_info.get('location', 'N/A')}")
                        if personal_info.get("linkedin"):
                            st.markdown(f"**LinkedIn:** [{personal_info['linkedin']}]({personal_info['linkedin']})")
                        if personal_info.get("github"):
                            st.markdown(f"**GitHub:** [{personal_info['github']}]({personal_info['github']})")
                        if personal_info.get("portfolio"):
                            st.markdown(f"**Portfolio:** [{personal_info['portfolio']}]({personal_info['portfolio']})")

                    analysis = results.get("analysis_results", {})
                    skills_analysis = analysis.get("skills_analysis", {})

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Experience", f"{skills_analysis.get('years_of_experience', 0)} years")
                    with col2:
                        st.metric("Level", skills_analysis.get("experience_level", "Unknown"))
                    with col3:
                        st.metric("Confidence", f"{analysis.get('confidence_score', 0):.0%}")

                    st.write("### Technical Skills")
                    skills = skills_analysis.get("technical_skills", [])
                    if skills:
                        st.write(", ".join(skills))
                    else:
                        st.write("No technical skills identified.")

                    st.write("**Education:**")
                    education = skills_analysis.get("education", [])
                    if education and len(education) > 0:
                        first_edu = education[0]
                        degree = first_edu.get('degree', 'Unknown')
                        institution = first_edu.get('institution', 'Unknown')
                        st.write(f"{degree} from {institution}")
                        if len(education) > 1:
                            st.write(f"(and {len(education)-1} more education entries)")
                    else:
                        st.write("No education information found.")

                    st.write("**Domain Expertise:**")
                    domains = skills_analysis.get("domain_expertise", [])
                    if domains:
                        st.write(", ".join(domains))
                    else:
                        st.write("No domains found.")

                with tab2:
                    st.subheader("Job Matches")
                    matching = results.get("match_results", {})
                    matched_jobs = matching.get("matched_jobs", [])
                    if matched_jobs:
                        for match in matched_jobs:
                            st.write(f"**{match['title']}** - Match Score: {match['match_score']}")
                            st.write(f"**Location:** {match.get('location', 'N/A')}")
                            st.write(f"**Salary:** {match.get('salary_range', 'N/A')}")
                            st.write(f"**Requirements:** {', '.join(match.get('requirements', []))}")
                            st.divider()
                    else:
                        st.write("No matches found.")

                with tab3:
                    st.subheader("Extracted Resume Data")
                    st.json(results.get("extracted_data", {}))

if __name__ == "__main__":
    main()