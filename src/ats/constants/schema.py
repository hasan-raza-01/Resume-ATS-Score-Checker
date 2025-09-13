# update __all__ 

from pydantic import BaseModel, Field 
from datetime import datetime


class Constants:
    ...

class DataIngestionConstants(BaseModel):
    TIME_STAMP: datetime = Field()
    ROOT_DIR_NAME: str = Field(frozen=True) 
    DATA_ROOT_DIR_NAME: str = Field(frozen=True) 
    INGESTION_ROOT_DIR_NAME: str = Field(frozen=True) 
    RAW_DATA_DIR_NAME: str = Field(frozen=True)
    OUTPUT_DIR_NAME: str = Field(frozen=True)

class DataTransformationConstants(BaseModel):
    TIME_STAMP: datetime = Field()
    ROOT_DIR_NAME: str = Field(frozen=True) 
    DATA_ROOT_DIR_NAME: str = Field(frozen=True) 
    TRANSFORMATION_ROOT_DIR_NAME: str = Field(frozen=True) 
    PARSED_DATA_DIR_NAME: str = Field(frozen=True)
    STRUCTURED_DATA_DIR_NAME: str = Field(frozen=True)
    TRAIN_DATA_DIR_NAME: str = Field(frozen=True)
    OUTPUT_DIR_NAME: str = Field(frozen=True)


__all__ = ["DataIngestionConstants", "DataTransformationConstants", "Constants", ]