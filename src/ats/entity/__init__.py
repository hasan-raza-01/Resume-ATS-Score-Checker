# update __all__ 

from pydantic import BaseModel
from datetime import datetime
from pathlib import Path 


class DataIngestion(BaseModel):
    TIME_STAMP: datetime
    ROOT_DIR_PATH: Path
    DATA_ROOT_DIR_PATH: Path
    INGESTION_ROOT_DIR_PATH: Path
    RAW_DATA_DIR_PATH: Path
    OUTPUT_DIR_PATH: Path

class DataTransformation(BaseModel):
    PROMPT: str
    TIME_STAMP: datetime
    ROOT_DIR_PATH: Path
    DATA_ROOT_DIR_PATH: Path
    TRANSFORMATION_ROOT_DIR_PATH: Path
    PARSED_DATA_DIR_PATH: Path
    STRUCTURED_DATA_DIR_PATH: Path
    TRAIN_DATA_DIR_PATH: Path
    OUTPUT_DIR_PATH: Path

class JobDescription(BaseModel):
    TIME_STAMP: datetime
    ROOT_DIR_PATH: Path
    JD_ROOT_DIR_PATH: Path

class Scoring(BaseModel):
    TIME_STAMP: datetime
    ROOT_DIR_PATH: Path
    SCORES_ROOT_DIR_PATH: Path
    SCORING_DATA_DIR_PATH: Path
    OUTPUT_DIR_PATH: Path

__all__ = ["DataIngestion", "DataTransformation", "JobDescription", "Scoring"]