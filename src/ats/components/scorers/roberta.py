from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Dict, Set
from ... import logging
from ...exception import CustomException
import sys
import re

class RoBERTaHybridScorer:
    def __init__(self):
        # High-quality 1024-dimensional model
        self.semantic_model = SentenceTransformer('sentence-transformers/all-roberta-large-v1')
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 3))
        
    def extract_keywords(self, text: str) -> Set[str]:
        """Extract important keywords and phrases"""
        try:
            # Technical terms pattern
            tech_pattern = r'\b(?:python|javascript|react|docker|kubernetes|aws|azure|gcp|ml|ai|api|sql|nosql|git|ci/cd|devops|microservices|fastapi|django|flask|pandas|numpy|tensorflow|pytorch|scikit|machine learning|deep learning|data science|backend|frontend|full.stack|senior|junior|lead|architect|engineer|developer|analyst|manager)\b'

            keywords = set()

            # Extract technical keywords
            tech_matches = re.findall(tech_pattern, text.lower())
            keywords.update(tech_matches)

            # Extract skill-related phrases
            skill_phrases = re.findall(r'\b(?:\w+(?:\s+\w+){0,2})\s+(?:experience|skills?|expertise|proficiency|knowledge|familiar)\b', text.lower())
            keywords.update(skill_phrases)

            return keywords
        except Exception as e:
            e = CustomException(e, sys)
            logging.error(e)
            raise e
    
    def calculate_keyword_overlap(self, resume_text: str, job_text: str) -> float:
        """Calculate keyword-based matching score"""
        try:
            resume_keywords = self.extract_keywords(resume_text)
            job_keywords = self.extract_keywords(job_text)

            if not job_keywords:
                return 0.0

            overlap = resume_keywords.intersection(job_keywords)
            overlap_score = len(overlap) / len(job_keywords) if job_keywords else 0

            return overlap_score * 100
        except Exception as e:
            if not isinstance(e, CustomException):
                e = CustomException(e, sys)
            logging.error(e)
            raise e
    
    def create_comprehensive_text(self, resume_data: Dict) -> str:
        """Create comprehensive text representation"""
        try:
            sections = []

            # Professional identity
            if resume_data.get('professional_summary'):
                prof = resume_data['professional_summary']
                if prof.get('headline'):
                    sections.append(f"Professional role: {prof['headline']}")
                if prof.get('summary'):
                    sections.append(f"Professional summary: {prof['summary']}")
                if prof.get('total_experience_years'):
                    sections.append(f"Years of experience: {prof['total_experience_years']}")

            # Detailed work experience
            if resume_data.get('work_experience'):
                for exp in resume_data['work_experience']:
                    exp_parts = []
                    if exp.get('title') and exp.get('company'):
                        exp_parts.append(f"Worked as {exp['title']} at {exp['company']}")

                    if exp.get('responsibilities'):
                        exp_parts.append(f"Key responsibilities included: {' | '.join(exp['responsibilities'])}")

                    if exp.get('achievements'):
                        exp_parts.append(f"Key achievements: {' | '.join(exp['achievements'])}")

                    if exp.get('technologies_used'):
                        exp_parts.append(f"Technologies and tools used: {', '.join(exp['technologies_used'])}")

                    if exp_parts:
                        sections.append(' '.join(exp_parts))

            # Comprehensive skills
            if resume_data.get('skills'):
                skills = resume_data['skills']
                if skills.get('technical'):
                    sections.append(f"Technical skills and expertise: {', '.join(skills['technical'])}")
                if skills.get('soft'):
                    sections.append(f"Soft skills and capabilities: {', '.join(skills['soft'])}")
                if skills.get('certifications'):
                    sections.append(f"Professional certifications: {', '.join(skills['certifications'])}")

            # Educational background
            if resume_data.get('education'):
                for edu in resume_data['education']:
                    if edu.get('degree') and edu.get('institution'):
                        sections.append(f"Educational background: {edu['degree']} from {edu['institution']}")

            return ' | '.join(sections)
        except Exception as e:
            e = CustomException(e, sys)
            logging.error(e)
            raise e
        
    def create_comprehensive_job_text(self, job_data: Dict) -> str:
        """Create comprehensive job description text"""
        try:
            sections = []

            sections.append(f"Job position: {job_data['job_title']} at {job_data['company_name']}")
            sections.append(f"Experience level required: {job_data['experience_level']}")
            sections.append(f"Job overview: {job_data['job_description']}")
            sections.append(f"Essential requirements and qualifications: {job_data['requirements']}")
            sections.append(f"Key responsibilities and duties: {job_data['responsibilities']}")

            if job_data.get('salary_range'):
                sections.append(f"Compensation: {job_data['salary_range']}")

            return ' | '.join(sections)
        except Exception as e:
            e = CustomException(e, sys)
            logging.error(e)
            raise e
    
    async def calculate_hybrid_score(self, resume_data: Dict, job_data: Dict) -> Dict:
        """Advanced hybrid scoring combining semantic and keyword matching"""
        logging.info("In RoBERTa")
        try:
            resume_text = self.create_comprehensive_text(resume_data)
            job_text = self.create_comprehensive_job_text(job_data)

            # 1. Semantic similarity using RoBERTa
            resume_embedding = self.semantic_model.encode([resume_text])
            job_embedding = self.semantic_model.encode([job_text])
            semantic_score = float(cosine_similarity(resume_embedding, job_embedding)[0][0] * 100)

            # 2. Keyword overlap score
            keyword_score = self.calculate_keyword_overlap(resume_text, job_text)

            # 3. TF-IDF based similarity (for term frequency importance)
            try:
                tfidf_matrix = self.tfidf_vectorizer.fit_transform([resume_text, job_text])
                tfidf_similarity = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0] * 100)
            except:
                tfidf_similarity = 0.0

            # 4. Experience level matching
            experience_score = 0.0
            if resume_data.get('professional_summary', {}).get('total_experience_years'):
                resume_exp = resume_data['professional_summary']['total_experience_years']
                job_level = job_data['experience_level'].lower()

                if job_level == 'entry' and resume_exp <= 2:
                    experience_score = 100.0
                elif job_level == 'junior' and 1 <= resume_exp <= 3:
                    experience_score = 100.0
                elif job_level == 'mid' and 3 <= resume_exp <= 6:
                    experience_score = 100.0
                elif job_level == 'senior' and resume_exp >= 5:
                    experience_score = 100.0
                else:
                    # Partial scoring for close matches
                    experience_score = max(0, 100 - abs(resume_exp - 5) * 10)  # Assume 5 years as baseline

            # Weighted hybrid score
            weights = {
                'semantic': 0.4,      # 40% - semantic understanding
                'keyword': 0.3,       # 30% - keyword matching
                'tfidf': 0.2,         # 20% - term frequency importance
                'experience': 0.1     # 10% - experience level fit
            }

            hybrid_score = (
                semantic_score * weights['semantic'] +
                keyword_score * weights['keyword'] +
                tfidf_similarity * weights['tfidf'] +
                experience_score * weights['experience']
            )
            logging.info("Out RoBERTa")
            return {
                'overall_score': hybrid_score,
                'score_breakdown': {
                    'semantic_similarity': semantic_score,
                    'keyword_overlap': keyword_score,
                    'tfidf_similarity': tfidf_similarity,
                    'experience_match': experience_score
                },
                'match_quality': 'Excellent' if hybrid_score > 80 else 'Good' if hybrid_score > 60 else 'Fair' if hybrid_score > 40 else 'Poor',
                'model_used': 'all-roberta-large-v1-hybrid',
                'recommendation': self._generate_recommendation(hybrid_score, {
                    'semantic_similarity': semantic_score,
                    'keyword_overlap': keyword_score,
                    'tfidf_similarity': tfidf_similarity,
                    'experience_match': experience_score
                })
            }
        except Exception as e:
            if not isinstance(e, CustomException):
                e = CustomException(e, sys)
            logging.error(e)
            raise e
        
    def _generate_recommendation(self, overall_score: float, breakdown: Dict) -> str:
        """Generate actionable recommendations"""
        if overall_score > 80:
            return "Excellent match - Strong candidate for this position"
        elif breakdown['keyword_overlap'] < 30:
            return "Consider updating resume with more relevant technical keywords"
        elif breakdown['semantic_similarity'] < 50:
            return "Resume content doesn't align well with job responsibilities"
        elif breakdown['experience_match'] < 60:
            return "Experience level may not be optimal for this role"
        else:
            return "Good potential - consider for interview with some reservations"

__all__ = ["RoBERTaHybridScorer"]