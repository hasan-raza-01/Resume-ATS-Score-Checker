# from src.ats.constants import load_constants 
# update __all__ also inside __init__ 

from src.ats.constants import * 
from dataclasses import dataclass 
from pathlib import Path 
import os 


constants = load_constants(["DataIngestion", ])

@dataclass(frozen=True)
class DataIngestionConfig:
    CONFIG = constants["DataIngestion"]
    ROOT_DIR_PATH = Path(CONFIG.ROOT_DIR_NAME)
    DATA_ROOT_DIR_PATH = Path(os.path.join(ROOT_DIR_PATH, CONFIG.DATA_ROOT_DIR_NAME))
    INGESTION_ROOT_DIR_PATH = Path(os.path.join(DATA_ROOT_DIR_PATH, CONFIG.INGESTION_ROOT_DIR_NAME))
    RAW_DATA_DIR_PATH = Path(os.path.join(INGESTION_ROOT_DIR_PATH, CONFIG.RAW_DATA_DIR_NAME))
    PARSED_DATA_DIR_PATH = Path(os.path.join(INGESTION_ROOT_DIR_PATH, CONFIG.PARSED_DATA_DIR_NAME)) 
    FINAL_DATA_DIR_PATH = Path(os.path.join(INGESTION_ROOT_DIR_PATH, CONFIG.FINAL_DATA_DIR_NAME)) 


__all__ = ["DataIngestionConfig", ]