import sqlite3
import json
from typing import Dict, Any,List
class JobDatabase:
    def __init__(self,db_path:str="db/jobs.sqlite"):
        """
        Initialize the database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.create_tables()
    def create_tables(self):
        """Create necessary tables if they don't exist.
        This runs automatically when JobDatabase() is created.

        """
        # Create tables for jobs, candidates, and applications
        with sqlite3.connect(self.db_path) as conn:
            #cursor for executing SQL commands
            cursor = conn.cursor()
            # Create jobs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT,
                    type TEXT,
                    experience_level TEXT,
                    salary_range TEXT,
                    description TEXT,
                    requirements TEXT,
                    benefits TEXT,
                    posted_date TEXT
                )
            ''')
            conn.commit()
            print("✅ Database table created/verified")
            #adds one job to database and return an id for that job
    def add_job(self, job_data: Dict[str, Any]) -> int:
        """ Add a single job to the database."""
        #Opens a database connection.
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            #SQL INSERT command to add a new row.
            cursor.execute('''
                INSERT INTO jobs (title, company, location, type, experience_level, salary_range, description, requirements, benefits, posted_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_data.get('title'),
                job_data.get('company'),
                job_data.get('location'),
                job_data.get('type'),
                job_data.get('experience_level'),
                job_data.get('salary_range'),
                job_data.get('description'),
                json.dumps(job_data.get('requirements', [])),  # Store list as JSON string
                json.dumps(job_data.get('benefits', [])),  # Store list as JSON string
                job_data.get('posted_date')
            ))
            conn.commit()
            return cursor.lastrowid
    #Get all jobs from database
    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """ Retrieve all jobs from the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM jobs')
            rows = cursor.fetchall()
            # Convert rows to list of dictionaries
            jobs = []
            for row in rows:
                jobs.append({
                    'id': row[0],
                    'title': row[1],
                    'company': row[2],
                    'location': row[3],
                    'type': row[4],
                    'experience_level': row[5],
                    'salary_range': row[6],
                    'description': row[7],
                    'requirements': json.loads(row[8]),  # Convert JSON string back to list
                    'benefits': json.loads(row[9]),  # Convert JSON string back to list
                    'posted_date': row[10]
                })
            return jobs
    def clear_all_jobs(self):
        """Delete all jobs from the database (useful for testing)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM jobs")
            conn.commit()
            print("🗑️ All jobs cleared")