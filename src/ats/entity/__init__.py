# update __all__ 

from dataclasses import dataclass
from pathlib import Path 

@dataclass
class DataIngestion:
    ROOT_DIR_PATH: Path
    REPORTS_DIR_PATH: Path
    DATA_ROOT_DIR_PATH: Path
    INGESTION_ROOT_DIR_PATH: Path
    RAW_DATA_DIR_PATH: Path
    SCHEMA_DATA_DIR_PATH: Path

__all__ = ["DataIngestion", ]