from typing import Dict, List

import pandas as pd

from jobspy import Site, scrape_jobs


class JobSpyScraper:
    """JobSpy-based scraper adapter that returns the same job shape as the Keejob scraper."""

    def __init__(self):
        self.default_sites = [
            Site.GOOGLE,
            Site.INDEED,
            Site.ZIP_RECRUITER,
            Site.LINKEDIN,
        ]

    def search_jobs(self, keyword: str = "", location: str = "", max_jobs: int = 15, country: str = "usa") -> List[Dict]:
        search_term = keyword.strip() if keyword else None
        normalized_country = (country or "usa").strip().lower()

        country_aliases = {
            "usa": "usa",
            "us": "usa",
            "united states": "usa",
            "canada": "canada",
            "uk": "uk",
            "united kingdom": "uk",
            "france": "france",
            "germany": "germany",
            "india": "india",
            "tunisia": "tunisia",
            "remote": "remote",
        }
        mapped_country = country_aliases.get(normalized_country, normalized_country)

        # Always prioritize selected country for search location to avoid CV-location override.
        search_location = None if mapped_country == "remote" else mapped_country.title()

        # If user selected remote, let a concrete CV location help ranking when available.
        if mapped_country == "remote" and location:
            search_location = location.strip()

        indeed_supported = {"usa", "canada", "uk", "france", "germany", "india"}
        if mapped_country in indeed_supported:
            site_list = self.default_sites
            country_indeed = mapped_country
        else:
            # Avoid silently searching USA for unsupported countries (e.g. Tunisia).
            site_list = [site for site in self.default_sites if site != Site.INDEED]
            country_indeed = None

        try:
            scrape_kwargs = {
                "site_name": site_list,
                "search_term": search_term,
                "location": search_location,
                "results_wanted": max_jobs,
                "description_format": "markdown",
                "verbose": 0,
            }
            if country_indeed:
                scrape_kwargs["country_indeed"] = country_indeed

            df = scrape_jobs(
                **scrape_kwargs,
            )
        except Exception as exc:
            print(f"⚠️ JobSpy search failed: {exc}")
            return []

        if df is None:
            return []

        if not isinstance(df, pd.DataFrame):
            try:
                df = pd.DataFrame(df)
            except Exception:
                return []

        jobs: List[Dict] = []
        for row in df.to_dict(orient="records"):
            job = self._normalize_job(row)
            if job:
                jobs.append(job)

        return jobs[:max_jobs]

    def _normalize_job(self, row: Dict) -> Dict:
        title = (
            row.get("job_title")
            or row.get("title")
            or row.get("position")
            or row.get("name")
            or "Unknown Position"
        )

        company = (
            row.get("company")
            or row.get("company_name")
            or row.get("hiring_organization")
            or row.get("employer")
            or "Company Not Listed"
        )

        location = row.get("location") or row.get("job_location") or row.get("city") or ""
        url = row.get("job_url") or row.get("url") or row.get("link") or ""
        description = (
            row.get("description")
            or row.get("job_description")
            or row.get("snippet")
            or ""
        )

        salary_parts = [
            row.get("min_amount"),
            row.get("max_amount"),
            row.get("salary_currency"),
        ]
        salary_values = [str(value).strip() for value in salary_parts if value not in (None, "")]
        salary_range = " ".join(salary_values) if salary_values else "Not specified"

        return {
            "title": str(title).strip(),
            "company": str(company).strip(),
            "location": str(location).strip() or "Location not specified",
            "url": str(url).strip(),
            "description": str(description).strip(),
            "requirements": self._extract_skills_from_text(f"{title} {description}"),
            "salary_range": salary_range,
            "source": f"JobSpy/{row.get('site', 'unknown')}",
        }

    def _extract_skills_from_text(self, text: str) -> List[str]:
        if not text:
            return []

        tech_keywords = [
            "Python", "Java", "JavaScript", "TypeScript", "C#", "C++", "PHP", "Ruby", "Go",
            "React", "Angular", "Vue", "Node.js", "Django", "Flask", "Spring", "Laravel",
            "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Oracle",
            "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Git", "Jenkins",
            "REST", "API", "GraphQL", "Microservices", "Agile", "Scrum",
            "Machine Learning", "AI", "Data Science", "DevOps", "CI/CD",
            "HTML", "CSS", "Sass", "TailwindCSS", "Bootstrap",
            "Express", "FastAPI", "NestJS", "Next.js", "React Native",
            "TensorFlow", "PyTorch", "Keras", "scikit-learn",
            "Linux", "Windows", "MacOS", "Android", "iOS",
        ]

        found_skills = []
        lowered_text = text.lower()
        for skill in tech_keywords:
            if skill.lower() in lowered_text:
                found_skills.append(skill)

        return found_skills
