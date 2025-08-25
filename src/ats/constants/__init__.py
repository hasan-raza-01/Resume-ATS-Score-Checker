# update required on 'Note: Available name' inside docstring of fuction 'load_constants' 
# update __all__ 

from .values import *
from src.ats.utils import load_yaml
from typing import Dict 
import os 



CONFIG = load_yaml(os.path.join("src", "ats", "config", "raw", "config.yaml")) 

def load_constants(name: str | list[str] | tuple[str]) -> Dict:
    """loads respective constants for the given name

    Args:
        name (str | list[str] | tuple[str]): name of required object 

        Note: Available name --> DataIngestion, 

    Returns:
        Dict: key = name of object used to load given in variable \'name\', 

              value = Object of the name used to load,

              example:
              output = load_constants("DataIngestion")
              output = { "DataIngestion" : DataIngestionConstants } 
              data_ingestion_constants = output["DataIngestion"] 
    """
    return load(CONFIG, name)


__all__ = ["load_constants", "CONFIG"]