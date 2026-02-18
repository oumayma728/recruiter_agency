import streamlit as st
import tempfile
#asyncio is for handling asynchronous operations, which allows the application to perform tasks without blocking the main thread
import asyncio
from agents.orchestrator_agent import OrchestratorAgent
from db.database import JobDatabase

def save_uploaded_file(uploaded_file):
    with tempfile.NamedTemporaryFile( #Creates a real temporary file on your disk
        delete=False, #keeps the file after closing it
        suffix=".pdf") as tmp_file: #create a temp file with .pdf suffix
        tmp_file.write(uploaded_file.read()) #write the uploaded file content to the temp file
        return tmp_file.name #return the path to the temp file

def load_job_database():
    """Load the job database and return a list of job postings."""
    db = JobDatabase() #create an instance of the JobDatabase class
    return db.get_all_jobs() #call the get_all_jobs method to retrieve all job postings from the database

async def process_resume(file_path:str, job_list:list)->dict:
    """Process the resume through the agent workflow and return the results."""
    try:
        orchestrator_agent = OrchestratorAgent() #create an instance of the orchestrator agent
        resume_data={
            "file_path": file_path,
            "job_list": job_list
        }
        result= await orchestrator_agent.process_resume(resume_data,job_list) #call the process_resume method of the orchestrator agent with the resume data and wait for the result
        return result #return the result of processing the resume
    except Exception as e:
        return {"error": str(e), "workflow_status": "failed"}
#UI
def main():
    st.set_page_config(page_title="AI Recruiter Agency", page_icon="🤖", layout="centered")
    st.title("🤖 AI Recruiter Agency")
    st.write("Upload a resume to find the best job matches based on skills and experience.")

    job_list = load_job_database() #load the job database to get the list of job postings
    if not job_list:
        st.error("No job postings found in the database. Please add some jobs before using the matching feature.")
        return
    st.info(f"Loaded {len(job_list)} job postings from the database.") #display the number of job postings loaded
    uploaded_file=st.file_uploader("Upload you CV ",type=["pdf"])

    if st.button("Find Matches"):
        if not uploaded_file:
            st.warning("Please upload a resume before finding matches.")
        else:
            file_path = save_uploaded_file(uploaded_file) #save the uploaded file and get its path
            st.success("Resume uploaded successfully! Processing...")
            with st.spinner("Analyzing resume and finding matches..."):
                results = asyncio.run(process_resume(file_path, job_list)) #process the resume and get the results
            if results.get("error"):
                st.error(f"Error processing resume: {results['error']}") #display any errors that occurred during processing
            else:
                st.success("Resume processed successfully! Here are the results:") #display a success message if processing was successful
                tab1,tab2,tab3=st.tabs(["Extracted Data","Analysis Results","Matched Jobs"]) #create tabs to display different parts of the results
                with tab1:
                    st.subheader("Candidate Analysis - Extracted Data")
                    analysis= results.get("analysis",{})
                    skills_analysis=analysis.get("skills_analysis",{})
                    col1,col2,col3=st.columns(3)
                    with col1:
                        st.metric(
                            "Experience",
                            f"{skills_analysis.get('years_of_experience', 0)} years"
                        )
                    with col2:
                        st.metric(
                            "Level",
                            skills_analysis.get("experience_level", "Unknown")
                        )
                    with col3:
                        # ↑ Third column
                        
                        st.metric(
                            "Confidence",
                            f"{analysis.get('confidence_score', 0):.0%}"
                        )
                    st.write("### Technical Skills")
                    skills = skills_analysis.get("technical_skills", [])

                    if skills:
                        st.write(", ".join(skills))
                    else:
                        st.write("No technical skills identified.")
                    st.write("**Domain Expertise:**")
                    domains = skills_analysis.get("domain_expertise", [])
                    
                    if domains:
                        st.write(", ".join(domains))
                    else:
                        st.write("No domains found")
                with tab2:
                    st.subheader("Job Matches")
                    matching=results.get("match_results",{})
                    matched_jobs = matching.get("matched_jobs", [])
                    if matched_jobs:
                        for match in matched_jobs:
                            st.write(f"**{match['title']}** - {match['location']} - Match Score: {match['match_score']}")
                            st.write(f"Requirements: {', '.join(match.get('requirements', []))}")
                            st.write(f"**Location:** {match.get('location', 'N/A')}")
                            st.write(f"**Salary:** {match.get('salary', 'N/A')}")

                    else:
                        st.write("No matches found.")
                with tab3:
                    st.subheader("Extracted Resume Data")
                    st.json(results.get("extracted_data",{})) #display the extracted data in JSON format

if __name__ == "__main__":
    main()


