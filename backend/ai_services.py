import os
from typing import List, Dict
import json
import re
import google.generativeai as genai

class AIService:
    def __init__(self):
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def calculate_job_match(self, user_skills: List[str], job_skills: List[str], job_description: str) -> float:
        """Calculate match score between user skills and job requirements"""
        try:
            prompt = f"""
            User Skills: {', '.join(user_skills)}
            Job Required Skills: {', '.join(job_skills)}
            Job Description: {job_description[:500]}

            Calculate a match score (0-100) based on:
            1. Direct skill matches (40%)
            2. Related/transferable skills (30%)
            3. Experience level fit (20%)
            4. Project complexity fit (10%)

            Return only the numerical score.
            """

            result = self.model.generate_content(prompt)
            score_text = result.text.strip()
            # Use raw string for regex pattern
            score = float(re.findall(r'\d+', score_text)[0])
            return min(100, max(0, score))

        except Exception as e:
            print(f"AI match calculation error: {e}")
            return 0.0

    def generate_proposal(self, user_data: Dict, job_data: Dict) -> str:
        """Generate a personalized proposal for a job"""
        try:
            prompt = f"""
            Create a professional freelance proposal for:

            Freelancer Profile:
            - Skills: {user_data.get('skills', '')}
            - Experience: {user_data.get('experience_level', '')}
            - Hourly Rate: ${user_data.get('hourly_rate', 0)}/hour

            Job Details:
            - Title: {job_data.get('title', '')}
            - Description: {job_data.get('description', '')[:300]}
            - Budget: ${job_data.get('budget', 'Not specified')}

            Write a compelling 150-200 word proposal that:
            1. Shows understanding of requirements
            2. Highlights relevant skills
            3. Includes a brief approach/timeline
            4. Ends with a call to action

            Keep it professional but personable.
            """

            result = self.model.generate_content(prompt)
            return result.text.strip()

        except Exception as e:
            print(f"AI proposal generation error: {e}")
            return "I'm interested in your project and believe my skills align well with your requirements. I'd love to discuss how I can help you achieve your goals."

    def get_pricing_suggestions(self, user_id: int, total_earnings: float, total_hours: float, current_rate: float) -> Dict:
        """Get AI-powered pricing suggestions"""
        try:
            prompt = f"""
            Freelancer Analysis:
            - Total Earnings: ${total_earnings}
            - Total Hours: {total_hours}
            - Current Average Rate: ${current_rate}/hour

            Based on this data, provide pricing strategy advice:
            1. Should they increase/decrease rates?
            2. What's a good target hourly rate?
            3. One actionable tip for pricing

            Format as JSON with keys: recommendation, target_rate, tip
            """

            result = self.model.generate_content(prompt)

            try:
                return json.loads(result.text)
            except json.JSONDecodeError:
                return {
                    "recommendation": "Consider reviewing your rates based on market standards",
                    "target_rate": current_rate * 1.1,
                    "tip": "Track your project success rate to optimize pricing"
                }

        except Exception as e:
            print(f"AI pricing suggestion error: {e}")
            return {"recommendation": "Unable to generate suggestions at this time"}

    def analyze_skill_gaps(self, user_skills: List[str], missed_job_skills: List[str]) -> List[Dict]:
        """Analyze skill gaps from missed opportunities"""
        try:
            all_missed_skills = []
            for skills_str in missed_job_skills:
                if skills_str:
                    all_missed_skills.extend([s.strip() for s in skills_str.split(',')])

            prompt = f"""
            User Current Skills: {', '.join(user_skills)}
            Skills from Missed Jobs: {', '.join(all_missed_skills[:20])}

            Identify the top 5 missing skills that would:
            1. Open the most new opportunities
            2. Command higher rates
            3. Are learnable in 1-3 months

            For each skill, provide:
            - skill name
            - priority score (1-10)
            - learning resource suggestion

            Format as JSON array.
            """

            result = self.model.generate_content(prompt)
            try:
                return json.loads(result.text)
            except json.JSONDecodeError:
                return [{"skill": "React", "priority": 8, "resource": "Online React course"}]

        except Exception as e:
            print(f"AI skill gap analysis error: {e}")
            return []

    def generate_communication_response(self, message_type: str, client_message: str, context: Dict) -> str:
        """Generate professional communication responses"""
        try:
            prompt = f"""
            Communication Type: {message_type}
            Client Message: "{client_message}"
            Context: {json.dumps(context)}

            Generate a professional, diplomatic response that:
            1. Addresses the client's concern
            2. Maintains a positive relationship
            3. Protects the freelancer's interests
            4. Suggests next steps if appropriate

            Keep it concise (2-3 sentences) and professional.
            """

            result = self.model.generate_content(prompt)
            return result.text.strip()

        except Exception as e:
            print(f"AI communication response error: {e}")
            return "Thank you for your message. I'll review this and get back to you shortly with a detailed response."
