# update __all__ also inside __init__ 
from dotenv import load_dotenv 
load_dotenv()

from .parsers import *
from copy import deepcopy
from .schema import FileInfo
from src.ats.exception import *
from src.ats import logging 
from fastapi import UploadFile 
from src.ats.entity import * 
from typing import Dict, List
from datetime import datetime
from pathlib import Path, PurePath
from src.ats.utils import asave_file
import sys, os, pymongo, asyncio, base64, json, aiofiles


class DataIngestionComponents:
    """usage: 
            ingestion = DataIngestionComponents()
            data = await ingestion
    """
    def __init__(self, config:DataIngestion, files: List[UploadFile]) -> None: 
        self.__stop_execution = False
        # validate data type
        # config 
        if not isinstance(config, DataIngestion):
            self.__stop_execution = True
            raise TypeError(f"\'config\' must be an instance of \'{DataIngestion}\'")
        self.__config = config
        self.__files = files
        # create required vars 
        self.__req_keys = [
            "min_size", 
            "min_len"
        ]
        self.__supported_docs = {
            ".pdf": {
                "min_size": 200,
                "min_len": 1500
            },
            ".docx": {
                "min_size": 10240,
                "min_len": 10000
            },
            ".html": {
                "min_size": 100,
                "min_len": 100
            }
        }
        self.__data = {} 
        self.__formatted_data = []
        self.__connection = False

    def __await__(self):
        return self.__main().__await__()
    
    async def __update__files(self):
        names = []
        read_tasks = []
        for file in self.__files:
            names.append(file.filename.strip().lower())
            read_tasks.append(asyncio.create_task(file.read()))
        contents = await asyncio.gather(*read_tasks, return_exceptions=True)
        self.__files = {name:content for name, content in list(zip(names, contents))}

    @property 
    def output(self) -> Dict[str, FileInfo]:
        "output to be return by class after execution, main(method[coroutine]) also returns the same"
        return self.__data

    @property
    def supported_docs(self) -> Dict[str, Dict[str, int]]:
        """values can be modified by extend_supported_docs(method)

        Returns:
            Dict[str, Dict[str, int]]: private attribute for supported docs
        """
        return self.__supported_docs
    
    def extend_supported_docs(self, docs:Dict[str, Dict[str, int]], update:bool = False) -> Dict[str, Dict[str, int]]:
        """extends private attribute for supported docs 

        Args:
            docs (Dict[str, Dict[str, int]]): 
                keys --> suffix/extension of file 

                value --> dict with keys min_size and min_len and value as bytes/lenght-of-charachters
                where min_size is minimum size required for files with suffix/extension(key of parent dict) to proceed
                and min_len is minimum number of binary characters (len(BinaryIO.read())) will be required for files with suffix/extension(key of parent dict) to proceed

            update (bool, optional): should be set to True if you want to update an existing key(suffix/extension) info in supported docs. Defaults to False.

        Raises:
            TypeError: if \'docs\' is not dict
            TypeError: if key of parent dict are not having value as dict
            ValueError: if sub dict is not having keys with name min_size and min_len 
            ValueError: if trying to modify existing key in attribute without passing arg \'update\' as \'True\'

        Returns:
            Dict[str, Dict[str, int]]: supported docs

        Example:
            supported_docs = {
                            ".pdf": {
                                "min_size": 200,
                                "min_len": 1500
                            }, 
                            ...
                        }
        """
        try:
            if not isinstance(docs, dict):
                raise TypeError(f"\'docs\' should be a dict object")
            for key in docs:
                if not isinstance(docs, dict):
                    raise TypeError(f"key should also be a dict object, with keys min_size, min_len")
                req_key_not_found = []
                for req_key in self.__req_keys:
                    if req_key not in key:
                        req_key_not_found.append(req_key)
                if req_key_not_found:
                    raise ValueError(f"not found keys \'{" ,".join(req_key_not_found)}\'")
                if not update:
                    if key in self.__supported_docs:
                        raise ValueError(f"arg \'update\' should be set to \'True\' in order to change value of existing key.")
            self.__supported_docs.update(docs)
            return self.__supported_docs
        except Exception as e:
            raise CustomException(e, sys)
    
    async def __validate(self):
        """performs basic validation before starting process

        Raises:
            FileTypeError: if type of file is not in supported_docs
            MinFileSizeError: _description_
            ValueError: _description_
        """
        loop = asyncio.get_running_loop()
        def func() -> None:
            if self.__stop_execution:
                logging.critical(f"__stop_execution={self.__stop_execution}, stoping execution. from __validate")
                return
            logging.info("In __validate")
            try:
                if self.__files:
                    for file in self.__files:
                        name = file.filename
                        info = FileInfo()
                        info.size = file.size
                        logging.info(f"checking \'{name}\'...")
                        suffix = Path(name).suffix.strip().lower()
                        try:
                            if suffix not in self.__supported_docs:
                                raise FileTypeError(suffix, "/".join([ext for ext in self.__supported_docs]))
                        except Exception as e:
                            info.status = False
                            e = CustomException(e, sys)
                            info.error.append(str(e))
                            logging.critical(str(e) + f" name={name}")
                        try:
                            if suffix in self.__supported_docs:
                                if info.size < self.__supported_docs[suffix]["min_size"]:
                                    raise MinFileSizeError(info.size, self.__supported_docs[suffix]["min_size"])
                        except Exception as e:
                            info.status = False
                            e = CustomException(e, sys)
                            info.error.append(str(e))
                            logging.critical(str(e) + f" name={name}")
                        self.__data[name] = info
                    logging.info("validation check completed.")
                else: 
                    raise ValueError(f"\'{len(self.__files)}\' files recieved.")
            except Exception as e:
                logging.error(str(CustomException(e, sys)))
                self.__stop_execution = True
            logging.info("out __validate")
        return await loop.run_in_executor(None, func)

    async def __base64_encode(self, content:bytes):
        loop = asyncio.get_running_loop()
        def encode():
            return base64.b64encode(content).decode("ascii")
        return await loop.run_in_executor(None, encode)

    async def __stage_and_format(self):
        "loads and saves data to staging dir and format data to insert into mongodb"
        if self.__stop_execution:
            logging.critical(f"__stop_execution={self.__stop_execution}, stoping execution. from __stage")
            return
        logging.info("In __stage_and_format")
        encode_tasks = []
        save_tasks = []
        files = []
        try:
            for name, content in self.__files.items():
                info = self.__data.get(name)
                if isinstance(content, Exception):
                    info.status = False
                    content = CustomException(content, sys)
                    info.error.append(str(content))
                    logging.critical(str(content) + f" name={name}")
                if info.status:
                    total_chars = len(content)
                    exp_total_chars = self.__supported_docs[Path(name).suffix.strip().lower()]["min_len"]
                    if total_chars < exp_total_chars:
                        raise MinContextError(total_chars, exp_total_chars)
                    # save file
                    path = self.__config.RAW_DATA_DIR_PATH.joinpath(name)
                    save_tasks.append(asyncio.create_task(asave_file(content, path)))
                    encode_tasks.append(asyncio.create_task(self.__base64_encode(content)))
                    files.append(name)

                else:
                    logging.critical(f"file-status={info.status}, skipping file \'{name}\'")
                self.__data[name] = info

            results = await asyncio.gather(*save_tasks, return_exceptions=True) 
            encodings = await asyncio.gather(*encode_tasks, return_exceptions=True)

            # update vars
            for name, result, encoding in list(zip(files, results, encodings)):
                info = self.__data.get(name)
                # update info 
                if info.status:
                    if isinstance(result, Exception):
                        info.status = False
                        result = CustomException(result, sys)
                        info.error.append(str(result))
                        logging.critical(str(result) + f" name={name}")
                    else:
                        info.path = result

                    if isinstance(encoding, Exception):
                        info.status = False
                        encoding = CustomException(encoding, sys)
                        info.error.append(str(encoding))
                        logging.critical(str(encoding) + f" name={name}")
                    else:
                        if encoding:
                            info.base64_size = len(encoding)
                            self.__formatted_data.append({"name":name, "data":encoding})
                        else:
                            logging.critical(f"len(encoding)={len(encoding)}, skipping file \'{name}\'")

                    # update __data and __files
                    if result.name != name:
                        self.__files[result.name] = self.__files.pop(name) 
                        self.__data[result.name] = info
                        self.__data.pop(name)
                else:
                    logging.critical(f"file-status={info.status}, skipping file \'{name}\'")
        except Exception as e:
            logging.error(str(CustomException(e, sys)))
            self.__stop_execution = True
        logging.info("Out __stage_and_format") 
        
    async def __connect(self) -> bool:
        """tries to connects with mongodb at given uri and return status

        Args:
            uri (str): mongodb uri for connection

        Returns:
            bool: True if successful else False
        """
        try:
            uri = os.getenv("MONGODB_URI")
            if not uri:
                raise EnvironmentError(f"missing evironment variable \'MONGODB_URI\'")
            self.__client = pymongo.AsyncMongoClient(uri)
            self.__database = self.__client[os.getenv("DATABASE", "xyz-task")]
            self.__collection = self.__database[os.getenv("COLLECTION", "xyz-operation")]
            self.__connection = True
            total_records = await self.__collection.count_documents({})
            logging.info(f"got connection, database=\'{self.__database.name}\', collection=\'{self.__collection.name}\', records={total_records}")
        except Exception as e: 
            logging.error(str(e))
            print(CustomException(e, sys))
            
    async def __ingest(self) -> None: 
        "Ingest data into mongodb if the connection is successfull"
        if self.__stop_execution:
            logging.critical(f"__stop_execution={self.__stop_execution}, stoping execution. from __ingest")
            return
        logging.info("In __ingest") 
        try:
            if self.__formatted_data:
                # wait to get connection with database
                await self.__connect()
                # operation
                if self.__connection:
                    result = await self.__collection.insert_many(self.__formatted_data)
                    ids = result.inserted_ids
                    records_inserted = len(ids)
                    total_records_for_insertion = len(self.__formatted_data)
                    total_records_in_db = await self.__collection.count_documents({})
                    remaining_records = total_records_for_insertion - records_inserted
                    logging.info(f"inserted:{records_inserted}/{total_records_for_insertion}, remaining:{remaining_records}, total records in db:{total_records_in_db}")
                else:
                    logging.warning(f"unable to connect with database={self.__database.name}, collection={self.__collection.name}, connection-status={self.__connection}")
            else:
                logging.warning(f"skipping data insertion as data having \'{len(self.__formatted_data)}\' records.")
        except Exception as e:
            logging.error(str(CustomException(e, sys)))
            self.__stop_execution = True
        logging.info("Out __ingest") 

    async def __main(self) -> Dict[str, FileInfo]:
        "controls the workflow"
        logging.info("In DataIngestion")
        # start workflow
        await self.__validate()
        # read all collected files after '__validate'
        await self.__update__files()
        # continue workflow 
        await self.__stage_and_format()
        await self.__ingest()
        data = {}
        errors = []
        i = 1
        for key in self.__data:
            try:
                info = deepcopy(self.__data[key])
                if isinstance(info.path, PurePath):
                    info.path = info.path.as_posix()
                    info.parsed_path = info.parsed_path.as_posix()
                    info.structured_path = info.structured_path.as_posix()
                data[key] = vars(info)
            except Exception as e:
                errors.append(str(i)+") "+str(e))
                i += 1
        try:
            self.__config.TIME_STAMP = datetime.now()
            timestamp = self.__config.TIME_STAMP.strftime("%d_%m_%Y_%H_%M_%S")
            path = self.__config.OUTPUT_DIR_PATH.joinpath(f"{timestamp}.json")
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            payload = json.dumps(data, ensure_ascii=False, indent=2)
            async with aiofiles.open(path, "w", encoding="utf-8", newline="\n") as f:
                await f.write(payload)
            logging.info(f"info saved at \'{path.as_posix()}\'")
        except Exception as e:
            errors.append(str(i)+") "+str(e))
        if errors:
            logging.error(f"error occured while persisting final data to disk, errors: \n{"\n".join(errors)}")
            print("DataIngestion Errors")
            print("--------------------")
            for error in errors:
                print(error)
        logging.info("Out DataIngestion")
        return self.__data
    
__all__ = ["DataIngestionComponents"]