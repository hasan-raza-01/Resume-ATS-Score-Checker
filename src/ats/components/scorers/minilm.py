from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import Dict, List, Tuple

class MiniLMResumeScorer:
    def __init__(self):
        # Fast and efficient model - 384 dimensions
        self.model = SentenceTransformer('sentence-transformers/paraphrase-MiniLM-L6-v2')
        self.batch_size = 32  # Optimized for speed
    
    def create_resume_sections(self, resume_data: Dict) -> List[str]:
        """Create focused sections for better matching"""
        sections = []
        
        # Core skills section
        if resume_data.get('skills', {}).get('technical'):
            sections.append(f"Technical expertise: {', '.join(resume_data['skills']['technical'])}")
        
        # Professional experience section
        if resume_data.get('work_experience'):
            exp_summary = []
            for exp in resume_data['work_experience']:
                if exp.get('title'):
                    exp_summary.append(f"{exp['title']}")
                if exp.get('technologies_used'):
                    exp_summary.append(f"using {', '.join(exp['technologies_used'])}")
            if exp_summary:
                sections.append(f"Experience: {' '.join(exp_summary)}")
        
        # Professional summary
        if resume_data.get('professional_summary', {}).get('summary'):
            sections.append(f"Profile: {resume_data['professional_summary']['summary']}")
            
        return sections
    
    def create_job_sections(self, job_data: Dict) -> List[str]:
        """Create job requirement sections"""
        sections = []
        
        sections.append(f"Role: {job_data['job_title']} requiring {job_data['experience_level']} level")
        sections.append(f"Key requirements: {job_data['requirements']}")
        sections.append(f"Main responsibilities: {job_data['responsibilities']}")
        
        return sections
    
    async def calculate_section_scores(self, resume_data: Dict, job_data: Dict) -> Dict:
        """Advanced section-wise scoring for better accuracy"""
        resume_sections = self.create_resume_sections(resume_data)
        job_sections = self.create_job_sections(job_data)
        
        if not resume_sections or not job_sections:
            return {'overall_score': 0.0, 'section_scores': {}}
        
        # Generate embeddings for all sections
        resume_embeddings = self.model.encode(resume_sections)
        job_embeddings = self.model.encode(job_sections)
        
        # Calculate cross-similarity matrix
        similarity_matrix = cosine_similarity(resume_embeddings, job_embeddings)
        
        # Advanced scoring logic
        section_scores = {}
        
        # Skills to requirements matching
        if len(resume_sections) > 0 and len(job_sections) > 1:
            section_scores['skills_to_requirements'] = float(similarity_matrix[0, 1] * 100)
        
        # Experience to responsibilities matching  
        if len(resume_sections) > 1 and len(job_sections) > 2:
            section_scores['experience_to_responsibilities'] = float(similarity_matrix[1, 2] * 100)
        
        # Overall best match
        overall_score = float(np.mean(np.max(similarity_matrix, axis=1)) * 100)
        
        return {
            'overall_score': overall_score,
            'section_scores': section_scores,
            'confidence': 'High' if overall_score > 70 else 'Medium' if overall_score > 45 else 'Low',
            'model_used': 'paraphrase-MiniLM-L6-v2',
            'processing_speed': 'Fast'
        }
    
    # async def batch_score_multiple(self, resume_list: List[Dict], job_data: Dict) -> List[Tuple[int, float]]:
    #     """Score multiple resumes against one job - optimized for speed"""
    #     results = []
        
    #     for i, resume in enumerate(resume_list):
    #         score_result = await self.calculate_section_scores(resume, job_data)
    #         results.append((i, score_result['overall_score']))
        
    #     # Return sorted by score (highest first)
    #     return sorted(results, key=lambda x: x[1], reverse=True)

__all__ = ["MiniLMResumeScorer"]