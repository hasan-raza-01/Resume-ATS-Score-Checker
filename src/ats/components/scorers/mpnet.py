from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict
from ... import logging
from ...exception import CustomException
import sys

class MPNetResumeScorer:
    def __init__(self):
        # Load the best quality pre-trained model
        self.model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        
    def extract_resume_text(self, resume_data: Dict) -> str:
        """Extract meaningful text from resume schema"""
        try:
            text_parts = []

            # Personal info
            if resume_data.get('personal_info'):
                if resume_data['personal_info'].get('name'):
                    text_parts.append(f"Name: {resume_data['personal_info']['name']}")

            # Professional summary
            if resume_data.get('professional_summary'):
                prof_summary = resume_data['professional_summary']
                if prof_summary.get('headline'):
                    text_parts.append(f"Professional Title: {prof_summary['headline']}")
                if prof_summary.get('summary'):
                    text_parts.append(f"Summary: {prof_summary['summary']}")
                if prof_summary.get('total_experience_years'):
                    text_parts.append(f"Experience: {prof_summary['total_experience_years']} years")

            # Work experience
            if resume_data.get('work_experience'):
                for exp in resume_data['work_experience']:
                    if exp.get('title') and exp.get('company'):
                        text_parts.append(f"Position: {exp['title']} at {exp['company']}")
                    if exp.get('responsibilities'):
                        text_parts.extend([f"Responsibility: {resp}" for resp in exp['responsibilities']])
                    if exp.get('technologies_used'):
                        text_parts.append(f"Technologies: {', '.join(exp['technologies_used'])}")

            # Skills
            if resume_data.get('skills'):
                if resume_data['skills'].get('technical'):
                    text_parts.append(f"Technical Skills: {', '.join(resume_data['skills']['technical'])}")
                if resume_data['skills'].get('certifications'):
                    text_parts.append(f"Certifications: {', '.join(resume_data['skills']['certifications'])}")

            # Education
            if resume_data.get('education'):
                for edu in resume_data['education']:
                    if edu.get('degree') and edu.get('institution'):
                        text_parts.append(f"Education: {edu['degree']} from {edu['institution']}")

            return " | ".join(text_parts)
        except Exception as e:
            e = CustomException(e, sys)
            logging.error(e)
            raise e
    
    def extract_job_text(self, job_data: Dict) -> str:
        """Extract meaningful text from job description schema"""
        try:
            text_parts = []

            text_parts.append(f"Job Title: {job_data['job_title']}")
            text_parts.append(f"Company: {job_data['company_name']}")
            text_parts.append(f"Experience Level: {job_data['experience_level']}")
            text_parts.append(f"Job Description: {job_data['job_description']}")
            text_parts.append(f"Requirements: {job_data['requirements']}")
            text_parts.append(f"Responsibilities: {job_data['responsibilities']}")
        
            return " | ".join(text_parts)
        except Exception as e:
            e = CustomException(e, sys)
            logging.error(e)
            raise e
    
    async def calculate_similarity_score(self, resume_data: Dict, job_data: Dict) -> float:
        """Calculate semantic similarity score between resume and job"""
        try:
            resume_text = self.extract_resume_text(resume_data)
            job_text = self.extract_job_text(job_data)
            
            # Generate embeddings
            resume_embedding = self.model.encode([resume_text])
            job_embedding = self.model.encode([job_text])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(resume_embedding, job_embedding)[0][0]
            
            # Convert to percentage score
            return float(similarity * 100)
        except Exception as e:
            if not isinstance(e, CustomException):
                e = CustomException(e, sys)
            logging.error(e)
            raise e
    
    async def get_detailed_score(self, resume_data: Dict, job_data: Dict) -> Dict:
        """Get detailed scoring breakdown"""
        logging.info("In MPNet")
        try:
            overall_score = await self.calculate_similarity_score(resume_data, job_data)

            # Section-wise scoring
            sections_score = {}

            # Skills matching
            if resume_data.get('skills') and resume_data['skills'].get('technical'):
                skills_text = f"Skills: {', '.join(resume_data['skills']['technical'])}"
                job_req_text = f"Requirements: {job_data['requirements']}"

                skills_emb = self.model.encode([skills_text])
                req_emb = self.model.encode([job_req_text])
                sections_score['skills_match'] = float(cosine_similarity(skills_emb, req_emb)[0][0] * 100)

            # Experience matching
            if resume_data.get('work_experience'):
                exp_texts = []
                for exp in resume_data['work_experience']:
                    if exp.get('responsibilities'):
                        exp_texts.extend(exp['responsibilities'])

                if exp_texts:
                    exp_text = " | ".join(exp_texts)
                    resp_text = job_data['responsibilities']

                    exp_emb = self.model.encode([exp_text])
                    resp_emb = self.model.encode([resp_text])
                    sections_score['experience_match'] = float(cosine_similarity(exp_emb, resp_emb)[0][0] * 100)
            logging.info("Out MPNet")
            return {
                'overall_score': overall_score,
                'sections_breakdown': sections_score,
                'match_level': 'High' if overall_score > 75 else 'Medium' if overall_score > 50 else 'Low',
                'model_used': 'all-mpnet-base-v2'
            }
        except Exception as e:
            if not isinstance(e, CustomException):
                e = CustomException(e, sys)
            logging.error(e)
            raise e

__all__ = ["MPNetResumeScorer"]