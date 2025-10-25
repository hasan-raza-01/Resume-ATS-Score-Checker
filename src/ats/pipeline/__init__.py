# update __all__

from fastapi import UploadFile 
from typing import List, Dict
from ..components import * 
from ..config import * 


class DataIngestionPipeline: 
    """pipeline for process of data ingestion 
    """
    async def run(self, files: List[UploadFile]) -> Dict[str, FileInfo]: 
        """runs data ingestion pipeline and returns the output

        Args:
            files (List[UploadFile]): list of intances of \'UploadFile\'

        Returns:
            Dict[str, FileInfo]: updated dict containing info of all files from current excecution
        """
        components = DataIngestionComponents(DataIngestionConfig, files) 
        return await components
    
class DataTransformationPipeline: 
    """pipeline for process of data transformation 
    """
    async def run(self, info: Dict[str, FileInfo] = None) -> tuple[Dict[str, ResumeSchema], Dict[str, FileInfo]]: 
        """runs data transformation pipeline and returns the output

        Args:
            info (Dict[str, FileInfo]): dict containing info of all files from previous excecution or \'None\', if None files will be loaded from disk, Defaults to None

        Returns:
            tuple[Dict[str, ResumeSchema], Dict[str, FileInfo]]: dict containing structured output of resume data, updated dict containing info of all files from current excecution
        """
        components = DataTransformationComponents(DataTransformationConfig, DataIngestionConfig, info) 
        return await components

class JobDescriptionPipeline: 
    """pipeline for extraction of job description 
    """
    async def run(self, url:str = None) -> JobDescription: 
        """runs job extraction pipeline and returns the object 'JobDescription'

        Args:
            url (str): url to extract job description, if None then there must be an environment variable named 'JD_URL', Defaults to None

        Returns:
            tuple[Dict[str, ResumeSchema], Dict[str, FileInfo]]: dict containing structured output of resume data, updated dict containing info of all files from current excecution
        """
        components = JobDescriptionComponents(JobDescriptionConfig, url) 
        return await components
    
class ScoringPipeline:
    """pipeline for scoring of resumes based on job description
    """
    async def run(self, resume_data: Dict[str, ResumeSchema], job_data: JobDescription, info: Dict[str, FileInfo]) -> tuple[Dict[str, FileInfo], Dict[str, Dict]]:
        """runs scoring pipeline and returns files info and scorings

        Args:
            resume_data (Dict[str, ResumeSchema]): resume data with respect to file names
            job_data (JobDescription): job description extracted from url
            info (Dict[str, FileInfo]): files info during execution

        Returns:
            tuple[Dict[str, FileInfo], Dict[str, Dict]]: tuple of files info and scorings dict
        """
        components = ScoringComponents(ScoringConfig, resume_data, job_data, info) 
        return await components

class CloudPushPipeline:
    """pipeline for pushing data from local directory/files to the cloud
    """
    async def run(self):
        components = CloudPushComponents(CloudPushConfig) 
        return await components

__all__ = ["DataIngestionPipeline", "DataTransformationPipeline", "JobDescriptionPipeline", "ScoringPipeline", "CloudPushPipeline"]
