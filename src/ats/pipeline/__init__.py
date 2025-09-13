# update __all__

from src.ats.components import * 
from fastapi import UploadFile 
from typing import List, Dict
from src.ats.config import * 


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
    async def run(self, info: Dict[str, FileInfo] | None = None) -> tuple[Dict[str, ResumeSchema], Dict[str, FileInfo]]: 
        """runs data transformation pipeline and returns the output

        Args:
            info (Dict[str, FileInfo]): dict containing info of all files from previous excecution or \'None\', Defaults to None

        Returns:
            tuple[Dict[str, ResumeSchema], Dict[str, FileInfo]]: dict containing structured output of resume data, updated dict containing info of all files from current excecution
        """
        components = DataTransformationComponents(DataTransformationConfig, DataIngestionConfig, info) 
        return await components


__all__ = ["DataIngestionPipeline", "DataTransformationPipeline", ]