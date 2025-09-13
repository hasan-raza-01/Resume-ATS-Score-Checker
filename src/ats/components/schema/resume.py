from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import List, Optional
import re


class PersonalInfo(BaseModel):
    name: str = Field(
        ...,  # Required field - no default
        min_length=1, 
        max_length=100,
        description="Full name of the person"
    )
    email: Optional[EmailStr] = Field(
        None,  # Make optional instead of empty string
        description="Valid email address"
    )
    phone: Optional[str] = Field(
        None,  # Make optional
        description="Phone number in any standard format"
    )
    location: Optional[str] = Field(
        None,
        description="City, State/Country location"
    )
    linkedin: Optional[str] = Field(
        None,
        description="LinkedIn profile URL or username"
    )
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v is None or v == "":
            return None
        # Basic phone validation - accept common formats
        if re.match(r'^[\+]?[\d\s\-\(\)]{7,20}$', v):
            return v
        raise ValueError('Invalid phone number format')


class ProfessionalSummary(BaseModel):
    headline: Optional[str] = Field(
        None,
        description="Professional headline or job title"
    )
    summary: Optional[str] = Field(
        None,
        description="Professional summary paragraph"
    )
    total_experience_years: Optional[int] = Field(
        None, 
        ge=0, 
        le=50,
        description="Total years of professional experience as integer"
    )
    career_level: Optional[str] = Field(
        None,
        description="Career level: entry, junior, mid, senior, or executive"
    )
    
    @field_validator('career_level')
    @classmethod
    def validate_career_level(cls, v):
        if v is None:
            return None
        valid_levels = ['entry', 'junior', 'mid', 'senior', 'executive']
        v_lower = v.lower().strip()
        if v_lower in valid_levels:
            return v_lower
        raise ValueError(f'Career level must be one of: {", ".join(valid_levels)}')


class WorkExperience(BaseModel):
    title: Optional[str] = Field(
        None,
        description="Job title"
    )
    company: Optional[str] = Field(
        None,
        description="Company name"
    )
    start_date: Optional[str] = Field(  # Changed from Union to just str
        None,
        description="Start date in any readable format (e.g., 'March 2019', '2019-03', 'Present')"
    )
    end_date: Optional[str] = Field(  # Changed from Union to just str
        None,
        description="End date in any readable format or 'Present' if currently employed"
    )
    duration_months: Optional[int] = Field(
        None, 
        ge=0,
        description="Duration in months as integer"
    )
    responsibilities: Optional[List[str]] = Field(
        None,
        description="List of key responsibilities"
    )
    achievements: Optional[List[str]] = Field(
        None,
        description="List of achievements and accomplishments"
    )
    technologies_used: Optional[List[str]] = Field(
        None,
        description="List of technologies, tools, and skills used"
    )


class Skills(BaseModel):
    technical: Optional[List[str]] = Field(
        None,
        description="List of technical skills and technologies"
    )
    soft: Optional[List[str]] = Field(
        None,
        description="List of soft skills and interpersonal abilities"
    )
    certifications: Optional[List[str]] = Field(
        None,
        description="List of professional certifications"
    )


class Education(BaseModel):
    degree: Optional[str] = Field(
        None,
        description="Degree type and field of study"
    )
    institution: Optional[str] = Field(
        None,
        description="Educational institution name"
    )
    graduation_year: Optional[int] = Field(
        None, 
        ge=1950, 
        le=2030,
        description="Graduation year as 4-digit integer"
    )
    gpa: Optional[str] = Field(
        None,
        description="GPA if available"
    )


class ResumeSchema(BaseModel):
    personal_info: PersonalInfo
    professional_summary: Optional[ProfessionalSummary] = None
    work_experience: Optional[List[WorkExperience]] = None
    skills: Optional[Skills] = None
    education: Optional[List[Education]] = None
    keywords: Optional[List[str]] = Field(
        None,
        description="List of relevant keywords from the resume"
    )


__all__ = ["ResumeSchema"]
