# from src.ats.constants import load_constants 
# update __all__ also inside __init__ 

from src.ats.constants import * 
from src.ats.entity import *
from pathlib import Path 
import os 


constants = load_constants(["DataIngestion", ])

DataIngestionConfig = DataIngestion(
    ROOT_DIR_PATH = Path(
        constants["DataIngestion"].ROOT_DIR_NAME),
    REPORTS_DIR_PATH = Path(os.path.join(
        constants["DataIngestion"].ROOT_DIR_NAME,
        constants["DataIngestion"].REPORTS_DIR_NAME)),
    SCHEMA_DATA_DIR_PATH = Path(os.path.join(
        constants["DataIngestion"].ROOT_DIR_NAME,
        constants["DataIngestion"].SCHEMA_DATA_DIR_NAME)),
    DATA_ROOT_DIR_PATH = Path(os.path.join(
        constants["DataIngestion"].ROOT_DIR_NAME, 
        constants["DataIngestion"].DATA_ROOT_DIR_NAME)),
    INGESTION_ROOT_DIR_PATH = Path(os.path.join(
        constants["DataIngestion"].ROOT_DIR_NAME, 
        constants["DataIngestion"].DATA_ROOT_DIR_NAME, 
        constants["DataIngestion"].INGESTION_ROOT_DIR_NAME)),
    RAW_DATA_DIR_PATH = Path(os.path.join(
        constants["DataIngestion"].ROOT_DIR_NAME, 
        constants["DataIngestion"].DATA_ROOT_DIR_NAME, 
        constants["DataIngestion"].INGESTION_ROOT_DIR_NAME, 
        constants["DataIngestion"].RAW_DATA_DIR_NAME))
)

__all__ = ["DataIngestionConfig", ]