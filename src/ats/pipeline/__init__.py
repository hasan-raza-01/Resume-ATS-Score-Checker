# update __all__

from src.ats.components import * 
from src.ats.config.builder import * 
from dataclasses import dataclass 
from typing import List, Dict 
from fastapi import UploadFile 


@dataclass 
class DataIngestionPipeline: 
    """pipeline for process of data ingestion 
    """
    def _run(self, files: List[UploadFile]) -> Dict[str, str]: 
        """runs data ingestion pipeline and returns the output

        Args:
            files (List[UploadFile]): list object of fastapi.UploadFile / files that have been uploaded

        Returns:
            Dict: 
            key = name of file 

            value = cleaned string object of parsed data  

            example:
            output = _run(files)
            output = {
                "xyz.pdf" : "cleaned_string_parsed_data_of_xyz.pdf", 
                "abc.docx": "cleaned_string_parsed_data_of_abc.docx", 
                ...
            } 
            name = output.keys()[0]
            data = output[name] 
        """
        components = DataIngestionComponents(DataIngestionConfig) 
        return components._main(files) 
    
__all__ = ["DataIngestionPipeline", ]