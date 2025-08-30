import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict

class JobScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_jobs(self) -> List[Dict]:
        """Scrape jobs from various sources"""
        all_jobs = []
        
        # Add delay to avoid being blocked
        time.sleep(random.uniform(1, 3))
        
        # Scrape from multiple sources
        all_jobs.extend(self.scrape_remoteok())
        all_jobs.extend(self.scrape_weworkremotely())
        all_jobs.extend(self.scrape_freelancer_reddit())
        
        return all_jobs
    
    def scrape_remoteok(self) -> List[Dict]:
        """Scrape jobs from RemoteOK"""
        jobs = []
        try:
            url = "https://remoteok.io/remote-freelance-jobs"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_elements = soup.find_all('tr', class_='job')
                
                for job in job_elements[:10]:  # Limit to 10 jobs
                    try:
                        title_elem = job.find('h2', class_='title')
                        company_elem = job.find('h3', class_='company')
                        
                        if title_elem and company_elem:
                            title = title_elem.get_text(strip=True)
                            company = company_elem.get_text(strip=True)
                            
                            jobs.append({
                                'title': title,
                                'description': f"Remote freelance position at {company}",
                                'required_skills': self.extract_skills_from_title(title),
                                'budget': None,
                                'source': 'remoteok',
                                'client_name': company,
                                'url': f"https://remoteok.io{job.get('data-href', '')}"
                            })
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"RemoteOK scraping error: {e}")
            
        return jobs
    
    def scrape_weworkremotely(self) -> List[Dict]:
        """Scrape jobs from WeWorkRemotely"""
        jobs = []
        try:
            url = "https://weworkremotely.com/remote-jobs/search?term=freelance"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_elements = soup.find_all('li', class_='feature')
                
                for job in job_elements[:5]:  # Limit to 5 jobs
                    try:
                        title_elem = job.find('span', class_='title')
                        company_elem = job.find('span', class_='company')
                        
                        if title_elem and company_elem:
                            title = title_elem.get_text(strip=True)
                            company = company_elem.get_text(strip=True)
                            
                            jobs.append({
                                'title': title,
                                'description': f"Remote opportunity with {company}",
                                'required_skills': self.extract_skills_from_title(title),
                                'budget': None,
                                'source': 'weworkremotely',
                                'client_name': company,
                                'url': 'https://weworkremotely.com' + job.find('a')['href'] if job.find('a') else None
                            })
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"WeWorkRemotely scraping error: {e}")
            
        return jobs
    
    def scrape_freelancer_reddit(self) -> List[Dict]:
        """Scrape freelance jobs from Reddit"""
        jobs = []
        try:
            url = "https://www.reddit.com/r/forhire.json?limit=10"
            response = requests.get(url, headers={**self.headers, 'User-Agent': 'FreelancerAI/1.0'})
            
            if response.status_code == 200:
                data = response.json()
                
                for post in data['data']['children']:
                    post_data = post['data']
                    title = post_data.get('title', '')
                    
                    # Only get hiring posts
                    if '[HIRING]' in title.upper():
                        jobs.append({
                            'title': title.replace('[HIRING]', '').strip(),
                            'description': post_data.get('selftext', '')[:300],
                            'required_skills': self.extract_skills_from_title(title),
                            'budget': self.extract_budget_from_text(post_data.get('selftext', '')),
                            'source': 'reddit',
                            'client_name': post_data.get('author', 'Reddit User'),
                            'url': f"https://reddit.com{post_data.get('permalink', '')}"
                        })
                        
        except Exception as e:
            print(f"Reddit scraping error: {e}")
            
        return jobs
    
    def extract_skills_from_title(self, title: str) -> List[str]:
        """Extract likely skills from job title"""
        common_skills = [
            'Python', 'JavaScript', 'React', 'Node.js', 'PHP', 'Laravel', 'Django',
            'HTML', 'CSS', 'WordPress', 'Shopify', 'SEO', 'Digital Marketing',
            'Data Analysis', 'Machine Learning', 'AI', 'Flutter', 'React Native',
            'iOS', 'Android', 'Unity', 'Game Development', 'Blockchain', 'Web3',
            'Graphic Design', 'UI/UX', 'Figma', 'Photoshop', 'Video Editing'
        ]
        
        found_skills = []
        title_lower = title.lower()
        
        for skill in common_skills:
            if skill.lower() in title_lower:
                found_skills.append(skill)
                
        return found_skills if found_skills else ['General']
    
    def extract_budget_from_text(self, text: str) -> float:
        """Extract budget information from job text"""
        import re
        
        # Look for common budget patterns
        budget_patterns = [
            r'\$(\d+(?:,\d+)?(?:\.\d+)?)',
            r'(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:dollars?|\$)',
            r'budget:?\s*\$?(\d+(?:,\d+)?(?:\.\d+)?)',
            r'pay:?\s*\$?(\d+(?:,\d+)?(?:\.\d+)?)'
        ]
        
        for pattern in budget_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                try:
                    # Remove commas and convert to float
                    budget = float(matches[0].replace(',', ''))
                    if 10 <= budget <= 100000:  # Reasonable range
                        return budget
                except ValueError:
                    continue
                    
        return None
