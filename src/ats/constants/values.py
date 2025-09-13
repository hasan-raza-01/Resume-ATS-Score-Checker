# 3 things needed to be updated at a time [avl_cons, process, Note: Available name] 
# Note is inside docstring of function 'load' from this file and 'load_constants' inside __int__.py 
# update __all__ 

from .schema import *
from src.ats.exception import CustomException 
from typing import List, Tuple, Dict
from datetime import datetime
from box import ConfigBox
import sys 


def __ing__(CONFIG:ConfigBox) -> Constants:
    return DataIngestionConstants(
        TIME_STAMP = datetime.now(),
        ROOT_DIR_NAME = CONFIG.ROOT_DIR, 
        DATA_ROOT_DIR_NAME = CONFIG.DATA.ROOT_DIR, 
        INGESTION_ROOT_DIR_NAME = CONFIG.DATA.INGESTION.ROOT_DIR, 
        RAW_DATA_DIR_NAME = CONFIG.DATA.INGESTION.RAW_DATA_DIR,
        OUTPUT_DIR_NAME = CONFIG.DATA.INGESTION.OUTPUT_DIR
    )

def __transform__(CONFIG:ConfigBox) -> Constants:
    return DataTransformationConstants(
        TIME_STAMP = datetime.now(),
        ROOT_DIR_NAME = CONFIG.ROOT_DIR , 
        DATA_ROOT_DIR_NAME = CONFIG.DATA.ROOT_DIR , 
        TRANSFORMATION_ROOT_DIR_NAME = CONFIG.DATA.TRANSFORMATION.ROOT_DIR , 
        PARSED_DATA_DIR_NAME = CONFIG.DATA.TRANSFORMATION.PARSED_DATA_DIR ,
        STRUCTURED_DATA_DIR_NAME = CONFIG.DATA.TRANSFORMATION.STRUCTURED_DATA_DIR ,
        TRAIN_DATA_DIR_NAME = CONFIG.STRUCTURED_TRAINING.ROOT_DIR,
        OUTPUT_DIR_NAME = CONFIG.DATA.TRANSFORMATION.OUTPUT_DIR
    )

dataingestion = "DataIngestion"
datatransformation = "DataTransformation"

avl_cons = [
    dataingestion, 
    datatransformation, 
]
process = {
    dataingestion:__ing__,
    datatransformation:__transform__
} 

def load(config:ConfigBox, name: str | List[str] | Tuple[str]) -> Dict: 
    """loads respective constants for the given name

    Args:
        config (ConfigBox): configuration for the object
        name (str | List[str] | Tuple[str]): name of required object  

        Note: Available names --> DataIngestion, DataTransformation,  

    Raises:
        CustomException: Error shows with file name, line no and error message

    Returns:
        Dict: key = name of object used to load given in variable \'name\', 
        
              value = Object of the name used to load,

              example:
              output = load(config, "DataIngestion")
              output = { "DataIngestion" : DataIngestionConstants } 
              data_ingestion_constants = output["DataIngestion"] 
    """
    reqs:List[str] = []
    try:
        # validate type   
        if isinstance(name, str):
            reqs.append(name) 
        elif isinstance(name, List) or isinstance(name, Tuple):
            reqs += name 
        else:
            ValueError(f"Unsupported type {{{type(name)}}} for variable {{name}}") 

        # validate values 
        for req in reqs:
            if req not in avl_cons:
                ValueError(f"Unknown value provided in variable \'name\', {req}, name can only have values from {avl_cons}") 

        # run respective functions and return the output 
        output = {}
        for req in reqs: 
            func = process[req] 
            output[req] = func(config)

        return output
    except Exception as e: 
        raise CustomException(e, sys) 
    

__all__ = ["load"]