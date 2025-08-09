# update __all__ 

from pydantic import BaseModel 
from pathlib import Path 


class DataIngestion(BaseModel):
    ROOT_DIR_PATH: Path 
    DATA_ROOT_DIR_PATH: Path 
    INGESTION_ROOT_DIR_PATH: Path 
    RAW_DATA_DIR_PATH: Path 
    PARSED_DATA_DIR_PATH: Path  
    FINAL_DATA_DIR_PATH: Path


__all__ = ["DataIngestion", ]