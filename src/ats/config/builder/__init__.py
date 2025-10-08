# from src.ats.constants import load_constants 
# update __all__ also inside __init__ 

from ...constants import *
from ...entity import *
from pathlib import Path 
import os 



constants = load_constants(["DataIngestion", "DataTransformation", "JobDescription", "Scoring"])
ingestion = constants["DataIngestion"]
transformation = constants["DataTransformation"]
jd = constants["JobDescription"]
scoring = constants["Scoring"]


DataIngestionConfig = DataIngestion(
    TIME_STAMP = ingestion.TIME_STAMP,
    ROOT_DIR_PATH = Path(
        ingestion.ROOT_DIR_NAME),
    DATA_ROOT_DIR_PATH = Path(os.path.join(
        ingestion.ROOT_DIR_NAME, 
        ingestion.DATA_ROOT_DIR_NAME)),
    INGESTION_ROOT_DIR_PATH = Path(os.path.join(
        ingestion.ROOT_DIR_NAME, 
        ingestion.DATA_ROOT_DIR_NAME, 
        ingestion.INGESTION_ROOT_DIR_NAME)),
    RAW_DATA_DIR_PATH = Path(os.path.join(
        ingestion.ROOT_DIR_NAME, 
        ingestion.DATA_ROOT_DIR_NAME, 
        ingestion.INGESTION_ROOT_DIR_NAME, 
        ingestion.RAW_DATA_DIR_NAME)),
    OUTPUT_DIR_PATH = Path(os.path.join(
        ingestion.ROOT_DIR_NAME,
        ingestion.DATA_ROOT_DIR_NAME, 
        ingestion.INGESTION_ROOT_DIR_NAME, 
        ingestion.OUTPUT_DIR_NAME)),
)

DataTransformationConfig = DataTransformation(
    PROMPT = transformation.PROMPT,
    TIME_STAMP = transformation.TIME_STAMP,
    ROOT_DIR_PATH = Path(
        transformation.ROOT_DIR_NAME),
    DATA_ROOT_DIR_PATH = Path(os.path.join(
        transformation.ROOT_DIR_NAME,
        transformation.DATA_ROOT_DIR_NAME)),
    TRANSFORMATION_ROOT_DIR_PATH = Path(os.path.join(
        transformation.ROOT_DIR_NAME,
        transformation.DATA_ROOT_DIR_NAME,
        transformation.TRANSFORMATION_ROOT_DIR_NAME)),
    PARSED_DATA_DIR_PATH = Path(os.path.join(
        transformation.ROOT_DIR_NAME,
        transformation.DATA_ROOT_DIR_NAME,
        transformation.TRANSFORMATION_ROOT_DIR_NAME,
        transformation.PARSED_DATA_DIR_NAME)),
    STRUCTURED_DATA_DIR_PATH = Path(os.path.join(
        transformation.ROOT_DIR_NAME,
        transformation.DATA_ROOT_DIR_NAME,
        transformation.TRANSFORMATION_ROOT_DIR_NAME,
        transformation.STRUCTURED_DATA_DIR_NAME)),
    TRAIN_DATA_DIR_PATH = Path(os.path.join(
        transformation.TRAIN_DATA_DIR_NAME)),
    OUTPUT_DIR_PATH = Path(os.path.join(
        transformation.ROOT_DIR_NAME,
        transformation.DATA_ROOT_DIR_NAME, 
        transformation.TRANSFORMATION_ROOT_DIR_NAME, 
        transformation.OUTPUT_DIR_NAME)),
)

JobDescriptionConfig = JobDescription(
    TIME_STAMP = jd.TIME_STAMP,
    ROOT_DIR_PATH = Path(jd.ROOT_DIR_NAME),
    JD_ROOT_DIR_PATH = Path(os.path.join(
        jd.ROOT_DIR_NAME,
        jd.JD_ROOT_DIR_NAME
    ))
)

ScoringConfig = Scoring(
    TIME_STAMP = scoring.TIME_STAMP,
    ROOT_DIR_PATH = Path(scoring.ROOT_DIR_NAME),
    SCORES_ROOT_DIR_PATH = Path(os.path.join(
        scoring.ROOT_DIR_NAME,
        scoring.SCORES_ROOT_DIR_NAME
    )),
    SCORING_DATA_DIR_PATH = Path(os.path.join(
        scoring.ROOT_DIR_NAME,
        scoring.SCORES_ROOT_DIR_NAME,
        scoring.DATA_DIR_NAME
    )),
    OUTPUT_DIR_PATH = Path(os.path.join(
        scoring.ROOT_DIR_NAME,
        scoring.SCORES_ROOT_DIR_NAME,
        scoring.OUTPUT_DIR_NAME
    ))
)

__all__ = ["DataIngestionConfig", "DataTransformationConfig", "JobDescriptionConfig", "ScoringConfig"]