# update __all__ 

from pydantic import BaseModel, Field 


class DataIngestionConstants(BaseModel):
    ROOT_DIR_NAME: str = Field(frozen=True) 
    DATA_ROOT_DIR_NAME: str = Field(frozen=True) 
    INGESTION_ROOT_DIR_NAME: str = Field(frozen=True) 
    RAW_DATA_DIR_NAME: str = Field(frozen=True) 
    PARSED_DATA_DIR_NAME: str = Field(frozen=True) 
    # FINAL_DATA_DIR_NAME: str = Field(frozen=True) 


__all__ = ["DataIngestionConstants", ]