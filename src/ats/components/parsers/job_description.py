from dotenv import load_dotenv
load_dotenv()

from ..schema import JobDescription
from firecrawl import Firecrawl
from typing import Dict
import os
import asyncio

class JobDescriptionParser:
    
    def __init__(self, firecrawl_api_key: str = None) -> None:
        if not firecrawl_api_key:
            firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
        
        if not firecrawl_api_key:
            raise ValueError(f"argument 'firecrawl_api_key' is having value '{firecrawl_api_key}'")
        
        self.firecrawl = Firecrawl(api_key=firecrawl_api_key)
    
    async def extract_job_description(self, url: str):
        """Extract job description using Firecrawl's AI-powered extraction"""
        loop = asyncio.get_event_loop()
        
        def _scrape():
            try:
                result = self.firecrawl.scrape(
                    url,
                    formats=[{
                        "type": "json",
                        "schema": JobDescription.model_json_schema()
                    }],
                    only_main_content=True,
                    timeout=30000
                )
                
                if result.get('success'):
                    return result['data']['json']
                else:
                    print(f"Firecrawl extraction failed: {result}")
                    return None
                    
            except Exception as e:
                print(f"Error with Firecrawl: {str(e)}")
                return None
        
        return await loop.run_in_executor(None, _scrape)
    
    async def extract_job_description_with_prompt(self, url: str):
        """Alternative method using natural language prompt"""
        loop = asyncio.get_event_loop()
        
        def _scrape_with_prompt():
            try:
                result = self.firecrawl.scrape(
                    url,
                    formats=[{
                        "type": "json",
                        "prompt": """Extract the following information from this job posting:
                        - Job title
                        - Company name
                        - Location
                        - Job type (full-time, part-time, etc.)
                        - Experience level required
                        - Complete job description
                        - Requirements and qualifications
                        - Key responsibilities
                        - Salary range (if mentioned)
                        - Posted date (if available)

                        Return as structured JSON."""
                    }],
                    only_main_content=True
                )
                
                if result.get('success'):
                    return result['data']['json']
                else:
                    return None
                    
            except Exception as e:
                print(f"Error: {str(e)}")
                return None
        
        return await loop.run_in_executor(None, _scrape_with_prompt)
    
    async def parse(self, url: str) -> JobDescription | Dict | None:
        job_data = await self.extract_job_description(url)
        
        if not job_data:
            job_data = await self.extract_job_description_with_prompt(url)
        
        return job_data

__all__ = ["JobDescriptionParser"]
