# update __all__ 

from pydantic import BaseModel, Field 
from pathlib import Path 


class DataIngestion(BaseModel):
    ROOT_DIR_PATH: Path = Field(frozen=True) 
    DATA_ROOT_DIR_PATH: Path = Field(frozen=True) 
    INGESTION_ROOT_DIR_PATH: Path = Field(frozen=True) 
    RAW_DATA_DIR_PATH: Path = Field(frozen=True) 
    PARSED_DATA_DIR_PATH: Path = Field(frozen=True) 
    FINAL_DATA_DIR_PATH: Path = Field(frozen=True) 


__all__ = ["DataIngestion", ]