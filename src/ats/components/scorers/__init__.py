from .mpnet import *
from .minilm import *
from .roberta import *
from typing import Dict

class ResumeScorer:
    def __init__(self):
        self.fast_scorer = MiniLMResumeScorer()      # First-pass filtering
        self.quality_scorer = MPNetResumeScorer()    # Detailed analysis
        self.enterprise_scorer = RoBERTaHybridScorer()  # Final ranking
    
    async def score(self, resume_data: Dict, job_data: Dict) -> Dict:
        # Tier 1: Fast filtering (< 100ms)
        fast_result = await self.fast_scorer.calculate_section_scores(resume_data, job_data)
        if fast_result['overall_score'] > 30:  # Worth detailed analysis
            # Tier 2: Quality semantic matching (< 300ms)  
            quality_result = await self.quality_scorer.get_detailed_score(resume_data, job_data)
            if quality_result['overall_score'] > 50:  # Potential candidate
                # Tier 3: Comprehensive hybrid scoring (< 800ms)
                enterprise_result = await self.enterprise_scorer.calculate_hybrid_score(resume_data, job_data)
                return enterprise_result
            else:
                return quality_result
        else:
            return fast_result

__all__ = ["ResumeScorer"]