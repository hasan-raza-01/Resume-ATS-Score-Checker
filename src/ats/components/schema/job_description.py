from pydantic import BaseModel, Field
from typing import Optional 


class JobDescription(BaseModel):
    job_title: str = Field(description="The job title")
    company_name: str = Field(description="The company name")
    location: str = Field(description="Job location")
    job_type: str = Field(description="Employment type (full-time, part-time, etc.)")
    experience_level: str = Field(description="Required experience level")
    job_description: str = Field(description="Complete job description text")
    requirements: str = Field(description="Job requirements and qualifications")
    responsibilities: str = Field(description="Key responsibilities")
    salary_range: Optional[str] = Field(description="Salary information if available")
    posted_date: Optional[str] = Field(description="When the job was posted")


__all__ = ["JobDescription", ]