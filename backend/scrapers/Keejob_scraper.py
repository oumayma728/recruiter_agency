# Selenium-based scraper for Keejob.com 
from selenium import webdriver 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from webdriver_manager.chrome import ChromeDriverManager 
from bs4 import BeautifulSoup 
import time 
import random 
from typing import List, Dict 
import urllib.parse 
 
class KeeJobScraper: 
    """Keejob scraper using Selenium with anti-detection""" 
 
    def __init__(self, headless=True): 
        self.base_url = "https://keejob.com" 
        self.search_url = f"{self.base_url}/offres-emploi" 
        self.driver = None 
        self.headless = headless 
 
    def _init_driver(self): 
        if self.driver: 
            return 
         
        chrome_options = Options() 
         
        if self.headless: 
            chrome_options.add_argument("--headless=new")  # Use new headless mode 
         
        # Anti-detection arguments 
        chrome_options.add_argument("--no-sandbox") 
        chrome_options.add_argument("--disable-dev-shm-usage") 
        chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
        chrome_options.add_argument("--disable-extensions") 
        chrome_options.add_argument("--disable-plugins") 
        chrome_options.add_argument("--disable-images") 
        chrome_options.add_argument("--start-maximized") 
         
        # Random user agent 
        user_agents = [ 
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36', 
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36', 
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36', 
        ] 
        chrome_options.add_argument(f'user-agent={random.choice(user_agents)}') 
         
        # Remove webdriver flag 
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
        chrome_options.add_experimental_option('useAutomationExtension', False) 
         
        service = Service(ChromeDriverManager().install()) 
        self.driver = webdriver.Chrome(service=service, options=chrome_options) 
         
        # Execute CDP commands to prevent detection 
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', { 
            "userAgent": random.choice(user_agents) 
        }) 
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 
         
        print("🌐 Browser started with anti-detection") 
 
    def search_jobs(self, keyword: str = "", location: str = "", max_jobs: int = 15) -> List[Dict]: 
        """Search jobs on Keejob with improved anti-detection""" 
         
        self._init_driver() 
        jobs = [] 
         
        try: 
            # Try different search strategies 
            search_strategies = [ 
                # Strategy 1: Direct search with keyword 
                lambda: self._search_with_keyword(keyword), 
                 
                # Strategy 2: Browse all jobs then filter 
                lambda: self._browse_all_jobs(), 
                 
                # Strategy 3: Try different URL format 
                lambda: self._search_alternative_format(keyword), 
                 
                # Strategy 4: Use category browsing 
                lambda: self._browse_by_category(keyword) 
            ] 
             
            for strategy in search_strategies: 
                try: 
                    jobs = strategy() 
                    if jobs: 
                        # Filter jobs by relevance if we have a keyword 
                        if keyword: 
                            jobs = self._filter_relevant_jobs(jobs, keyword) 
                        
                        if jobs:
                            print(f"✅ Found {len(jobs)} relevant jobs with current strategy") 
                            break 
                except Exception as e: 
                    print(f"⚠️ Strategy failed: {e}") 
                    continue 
             
            return jobs[:max_jobs] 
             
        except Exception as e: 
            print(f"❌ Search error: {e}") 
            return [] 
        finally: 
            self.close_browser() 
 
    def _search_with_keyword(self, keyword: str) -> List[Dict]: 
        """Strategy 1: Direct search with keyword""" 
        jobs = [] 
         
        # Encode keyword 
        encoded_keyword = urllib.parse.quote_plus(keyword) 
        url = f"{self.search_url}/?keywords={encoded_keyword}&professions=%5B%5D" 
         
        print(f"🔍 Strategy 1: Searching {url}") 
        self.driver.get(url) 
         
        # Random wait to simulate human behavior 
        time.sleep(random.uniform(3, 5)) 
         
        # Scroll slowly to load content 
        self._slow_scroll() 
         
        return self._extract_jobs_from_page() 
 
    def _search_alternative_format(self, keyword: str) -> List[Dict]: 
        """Strategy 3: Try alternative URL format""" 
        jobs = [] 
         
        encoded_keyword = urllib.parse.quote(keyword) 
        url = f"{self.base_url}/recherche?keywords={encoded_keyword}" 
         
        print(f"🔍 Strategy 3: Trying {url}") 
        self.driver.get(url) 
        time.sleep(random.uniform(3, 5)) 
        self._slow_scroll() 
         
        return self._extract_jobs_from_page() 
 
    def _browse_all_jobs(self) -> List[Dict]: 
        """Strategy 2: Browse all jobs and paginate""" 
        jobs = [] 
         
        print("🔍 Strategy 2: Browsing all jobs") 
        self.driver.get(self.search_url) 
        time.sleep(random.uniform(3, 5)) 
         
        # Try to get multiple pages 
        for page in range(1, 4):  # Try first 3 pages 
            if page > 1: 
                try: 
                    # Look for next page button 
                    next_buttons = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'Suivant')]") 
                    if next_buttons: 
                        next_buttons[0].click() 
                        time.sleep(random.uniform(2, 4)) 
                except: 
                    break 
             
            page_jobs = self._extract_jobs_from_page() 
            jobs.extend(page_jobs) 
            print(f"   Page {page}: Found {len(page_jobs)} jobs") 
         
        return jobs 
 
    def _browse_by_category(self, keyword: str) -> List[Dict]: 
        """Strategy 4: Browse by category based on keyword""" 
        jobs = [] 
         
        # Map keywords to categories 
        category_map = { 
            'developer': 'informatique', 
            'dev': 'informatique', 
            'software': 'informatique', 
            'it': 'informatique', 
            'data': 'informatique', 
            'marketing': 'commerce', 
            'commercial': 'commerce', 
            'finance': 'finance', 
            'comptable': 'finance' 
        } 
         
        # Find matching category 
        category = None 
        for key, cat in category_map.items(): 
            if key in keyword.lower(): 
                category = cat 
                break 
         
        if category: 
            url = f"{self.base_url}/offres-emploi/{category}" 
            print(f"🔍 Strategy 4: Browsing category {category}") 
            self.driver.get(url) 
            time.sleep(random.uniform(3, 5)) 
            jobs = self._extract_jobs_from_page() 
         
        return jobs 
 
    def _extract_jobs_from_page(self) -> List[Dict]: 
        """Extract jobs from current page with updated selectors""" 
        jobs = [] 
         
        # Get page source and parse 
        page_source = self.driver.page_source 
        soup = BeautifulSoup(page_source, "html.parser") 
         
        # Try multiple possible selectors for job cards (updated based on actual site) 
        job_card_selectors = [ 
            "article", 
            "article.bg-white", 
            "div.offre-item", 
        ] 
         
        job_cards = [] 
        for selector in job_card_selectors: 
            job_cards = soup.select(selector) 
            if job_cards: 
                print(f"   Found {len(job_cards)} cards with selector: '{selector}'") 
                break 
         
        if not job_cards: 
            # Save HTML for debugging 
            with open(f"debug_page_{int(time.time())}.html", "w", encoding="utf-8") as f: 
                f.write(page_source) 
            return [] 
         
        for card in job_cards: 
            try: 
                # Extract title - try multiple selectors 
                title = self._extract_text(card, [ 
                    "h2 a", "h2", "h3", "h4", 
                    ".job-title", ".poste", ".titre", 
                    "a[href*='/emploi/']", "a[href*='/offre/']" 
                ]) 
                 
                if not title or title == "Unknown Position": 
                    continue 
                 
                # Extract company 
                company = self._extract_text(card, [ 
                    "p a[href*='/companies/']", ".company", ".entreprise", ".employer", 
                    ".recruteur", ".societe", "span:-soup-contains('Chez')" 
                ]) 
                 
                # Extract location 
                location = ""
                loc_icon = card.select_one(".fa-map-marker-alt")
                if loc_icon and loc_icon.parent:
                    location = loc_icon.parent.get_text(strip=True)
                
                if not location:
                    location = self._extract_text(card, [ 
                        ".location", ".lieu", ".city", ".ville", 
                        "span:-soup-contains('Tunis')", "span:-soup-contains('Sfax')" 
                    ]) 
                 
                # Extract description 
                description = self._extract_text(card, [ 
                    "div.mb-3 p.text-sm", 
                    ".description", ".job-description", ".desc", 
                    ".resume", "p.text-sm"
                ]) 
                 
                # Extract date 
                date = ""
                date_icon = card.select_one(".fa-clock")
                if date_icon and date_icon.parent:
                    date = date_icon.parent.get_text(strip=True)
                
                if not date:
                    date = self._extract_text(card, [ 
                        ".date", "time", ".publié", ".published" 
                    ]) 
                 
                # Extract link 
                link_elem = card.find("a", href=True) 
                link = "" 
                if link_elem: 
                    link = link_elem['href'] 
                    if not link.startswith("http"): 
                        link = self.base_url + link 
                 
                job = { 
                    "title": title, 
                    "company": company or "Company Not Listed", 
                    "location": location or "Tunisia", 
                    "url": link, 
                    "description": description[:500] if description else "", 
                    "date_posted": date, 
                    "requirements": self._extract_skills_from_text(f"{title} {description}"), 
                    "salary_range": "Not specified", 
                    "source": "Keejob" 
                } 
                 
                jobs.append(job) 
                print(f"   ✅ Found: {title[:50]}...") 
                 
            except Exception as e: 
                continue 
         
        return jobs 
 
    def _extract_text(self, element, selectors, default=""): 
        """Helper to extract text using multiple selectors""" 
        for selector in selectors: 
            try: 
                found = element.select_one(selector) 
                if found and found.text.strip(): 
                    return found.text.strip() 
            except: 
                continue 
         
        # Try finding by text content 
        for selector in selectors: 
            try: 
                target_text = ""
                if "-soup-contains('" in selector:
                    target_text = selector.split("('")[1].split("')")[0]
                elif "contains('" in selector:
                    target_text = selector.split("('")[1].split("')")[0]
                
                if target_text:
                    found = element.find(string=lambda text: text and target_text in text) 
                    if found: 
                        return found.strip() 
            except: 
                continue 
         
        return default 
 
    def _slow_scroll(self): 
        """Slowly scroll down the page to load dynamic content""" 
        try: 
            total_height = self.driver.execute_script("return document.body.scrollHeight") 
            for i in range(0, total_height, 100): 
                self.driver.execute_script(f"window.scrollTo(0, {i});") 
                time.sleep(0.05) 
        except: 
            pass 
 
    def _filter_relevant_jobs(self, jobs: List[Dict], keyword: str) -> List[Dict]: 
        """Filter jobs by relevance to keyword""" 
        keyword_lower = keyword.lower() 
        # For small keywords like 'it', don't filter out
        keyword_parts = [p.lower() for p in keyword_lower.split() if len(p) > 1] 
        
        if not keyword_parts:
            return jobs
         
        relevant_jobs = [] 
        for job in jobs: 
            title = job.get('title', '').lower() 
            description = job.get('description', '').lower() 
             
            # Calculate relevance score 
            score = 0 
            for part in keyword_parts: 
                if part in title: 
                    score += 3  # Title match is worth more 
                elif part in description: 
                    score += 1  # Description match is worth less 
            
            # Special case for 'it' - usually it appears as 'IT' or in words. 
            # We already have title/description match which is fine.
            
            if score > 0: 
                job['relevance_score'] = score 
                relevant_jobs.append(job) 
         
        # Sort by relevance 
        relevant_jobs.sort(key=lambda x: x.get('relevance_score', 0), reverse=True) 
         
        return relevant_jobs 
 
    def _extract_skills_from_text(self, text: str) -> List[str]: 
        """Extract technical skills from job text""" 
        if not text: 
            return [] 
         
        tech_keywords = [ 
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C#', 'C++', 'PHP', 'Ruby', 'Go', 
            'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'Spring', 'Laravel', 
            'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Oracle', 
            'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Git', 'Jenkins', 
            'REST', 'API', 'GraphQL', 'Microservices', 'Agile', 'Scrum', 
            'Machine Learning', 'AI', 'Data Science', 'DevOps', 'CI/CD', 
            'HTML', 'CSS', 'Sass', 'TailwindCSS', 'Bootstrap', 
            'Express', 'FastAPI', 'NestJS', 'Next.js', 'React Native', 
            'TensorFlow', 'PyTorch', 'Keras', 'scikit-learn', 
            'Linux', 'Windows', 'MacOS', 'Android', 'iOS' 
        ] 
         
        found_skills = [] 
        text_lower = text.lower() 
         
        for skill in tech_keywords: 
            if skill.lower() in text_lower: 
                found_skills.append(skill) 
         
        return found_skills 
 
    def close_browser(self): 
        if self.driver: 
            self.driver.quit() 
            self.driver = None 
            print("🌐 Browser closed.")
