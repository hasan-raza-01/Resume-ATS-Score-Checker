# update required on 'Note: Available name' inside docstring of fuction 'load_constants' 
# update __all__ if needed

import os, yaml, aiofiles, asyncio
from box import ConfigBox
from typing import Dict 
from .values import *


async def get_config(path):
    async with aiofiles.open(path) as f:
        content = await f.read()
    dict_content = await asyncio.get_event_loop().run_in_executor(None, yaml.safe_load, content)
    return ConfigBox(dict_content)

path = os.path.join("src", "ats", "config", "raw", "config.yaml")
CONFIG = asyncio.run(get_config(path))

def load_constants(name: str | list[str] | tuple[str]) -> Dict:
    """loads respective constants for the given name

    Args:
        name (str | list[str] | tuple[str]): name of required object 

        Note: Available names --> DataIngestion, DataTransformation,

    Returns:
        Dict: key = name of object used to load given in variable \'name\', 

              value = Object of the name used to load,

              example:
              output = load_constants("DataIngestion")
              output = { "DataIngestion" : DataIngestionConstants } 
              data_ingestion_constants = output["DataIngestion"] 
    """
    return load(CONFIG, name)


__all__ = ["load_constants", ]