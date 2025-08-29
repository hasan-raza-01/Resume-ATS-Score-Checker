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
            Dict: shown below

            example:
            schema = _main(info)
            schema = {
                "path": path/of/the/file/in/disk,
                "size": size of the file in disk,
                "binary_content_size": total number of binary digits inside file (len(origin_data)),
                "base64_content_size": total number of base64 digits after converting from bytes to base64 string (len(base64_data))
            } 
            file_path = schema["path"]
            file_size = schema["size"]
            original_content_size = schema["binary_content_size"]
            converted_content_size = schema["base64_content_size"]
        """
        components = DataIngestionComponents(DataIngestionConfig) 
        return components._main(files) 
    
__all__ = ["DataIngestionPipeline", ]