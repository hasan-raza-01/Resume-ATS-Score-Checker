# from src.ats.constants import load_constants 
# update __all__ also inside __init__ 

from src.ats.constants import * 
from src.ats.entity import *
from pathlib import Path 
import os 


constants = load_constants(["DataIngestion", ])
CONFIG = constants["DataIngestion"]

DataIngestionConfig = DataIngestion(
    ROOT_DIR_PATH = Path(CONFIG.ROOT_DIR_NAME),
    DATA_ROOT_DIR_PATH = Path(os.path.join(CONFIG.ROOT_DIR_NAME, CONFIG.DATA_ROOT_DIR_NAME)),
    INGESTION_ROOT_DIR_PATH = Path(os.path.join(CONFIG.ROOT_DIR_NAME, CONFIG.DATA_ROOT_DIR_NAME, CONFIG.INGESTION_ROOT_DIR_NAME)),
    RAW_DATA_DIR_PATH = Path(os.path.join(CONFIG.ROOT_DIR_NAME, CONFIG.DATA_ROOT_DIR_NAME, CONFIG.INGESTION_ROOT_DIR_NAME, CONFIG.RAW_DATA_DIR_NAME)),
    PARSED_DATA_DIR_PATH = Path(os.path.join(CONFIG.ROOT_DIR_NAME, CONFIG.DATA_ROOT_DIR_NAME, CONFIG.INGESTION_ROOT_DIR_NAME, CONFIG.PARSED_DATA_DIR_NAME)), 
    FINAL_DATA_DIR_PATH = Path(os.path.join(CONFIG.ROOT_DIR_NAME, CONFIG.DATA_ROOT_DIR_NAME, CONFIG.INGESTION_ROOT_DIR_NAME, CONFIG.FINAL_DATA_DIR_NAME)) 
)

__all__ = ["DataIngestionConfig", ]