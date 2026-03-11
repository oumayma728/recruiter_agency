# 🤖 AI Recruitment Agents System

An intelligent **multi-agent system** designed to automate and optimize the recruitment workflow.  
Built with a **modular agent-based architecture**, where each agent is responsible for a specific task in the hiring pipeline.

---

## 📌 Overview

The system processes **resumes and job descriptions**, analyzes qualifications, matches candidates to roles, screens applications, enhances profiles, and recommends the best fits — all coordinated through a **central orchestrator**.  

Key features:

- **Scalable and maintainable architecture**  
- **Separation of concerns** for each agent  
- **AI-driven analysis** of candidate skills and job descriptions  
- Integration with **scrapers** like Keejob to fetch live job listings  

---

## 🔄 Workflow

Typical execution flow:

1. **Extractor Agent** → Extract structured data from resumes and job postings  
2. **Analyzer Agent** → Analyze candidate qualifications and skills  
3. **Profile Enhancer Agent** → Improve candidate profiles  
4. **Matcher Agent** → Compute candidate-job compatibility scores  
5. **Screener Agent** → Filter candidates based on requirements  
6. **Recommender Agent** → Recommend best-fit candidates  
7. **Orchestrator Agent** → Controls and coordinates the entire process  

---

## 🆕 Job Scraping Integration

The system now includes a **Keejob Scraper**:

- Fetches job listings from Keejob for live matching  
- Feeds the Matcher Agent with real-time job data  
- Supports integration with the **frontend JobMatches component**  

---

## ⚡ Tech Stack

- **Backend:** Python, FastAPI  
- **Frontend:** React, Tailwind CSS  
- **Scraping:** Keejob Scraper  
- **Database:** SQLite / PostgreSQL (configurable)  
- **AI/ML:** Candidate-job matching logic  

---

## 🚀 Getting Started

1. **Clone the repository** to your local machine.

2. **Backend setup (Python)**

   - Navigate to backend folder:
     ```bash
     cd backend
     ```
   - Create a virtual environment:

     **Windows**
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

     **Linux / Mac**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```

3. **Run the backend API**
   ```bash
   uvicorn main:app --reload
   ```
4. **Frontend setup (React + Tailwind)**
   ```bash
   cd ../frontend
   npm install
   npm start
    ```
