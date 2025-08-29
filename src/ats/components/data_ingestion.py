# update __all__ also inside __init__ 
from dotenv import load_dotenv 
load_dotenv()

from .parsers import *
from src.ats.utils import save_file, create_dirs, dump_json, bytes_to_b64str, load_json
from src.ats.exception import CustomException 
from dataclasses import dataclass 
from src.ats import logging 
from fastapi import UploadFile 
from src.ats.entity import * 
from typing import Dict, List 
import sys, os, pymongo
from copy import deepcopy
from datetime import datetime


@dataclass
class DataIngestionComponents: 
    data_ingestion_config: DataIngestion
    
    def __post_init__(self) -> None: 
        self.supported_ext = [".pdf", ".docx", ".html", ]

    def __load(self, files:List[UploadFile]) -> Dict[str, Dict[str, str]]: 
        """loads data, stores locally and returns name with path

        Args:
            files (List[UploadFile]): list object of fastapi.UploadFile / files that have been uploaded

        Raises:
            ValueError: if no files have been provided as argument

        Returns:
            Dict:
            key = name of file 

            value = dict of keys path, status, error(optional) 

            example:
            output = __load(files)
            output = {
                "xyz.pdf": {
                    path : "path/to/the/file", 
                    status: True | False, 
                    error(optional): error_details
                }, 
                "abc.docx": {
                    path : "path/to/the/file", 
                    status: True | False, 
                    error(optional): error_details
                } 
                ...
            } 
            name = output.keys()[0]
            file_info = output[name] 
            path = file_info["path"]
            status = file_info["status"]
            error = file_info["error"]
        """
        try:
            logging.info("In __load")
            files_len = len(files)
            if files_len > 0: 
                output = {}
                for file in files:
                    file_name = file.filename 
                    file_name = file_name.strip().lower() 
                    logging.info(f"working with \'{file_name}\'")
                    path = os.path.join(self.data_ingestion_config.RAW_DATA_DIR_PATH, file_name)
                    # save file
                    res = save_file(file.file, path)
                    # check weather file is supported or not
                    ext = os.path.splitext(file_name)[-1].lower()
                    if not ext in self.supported_ext:
                        raise ValueError(f"Unsupported file type: {file_name}")
                    del ext
                    logging.info(f"stagged \'{file_name}\'")
                    if isinstance(res, Exception):
                        output[file_name] = {"path": path, "status": False, "error": str(res)}
                    else:
                        dir_path, file_name = os.path.split(path)
                        file_name = res
                        path = os.path.join(dir_path, file_name)
                        output[file_name] = {"path": path, "status": True}
            else: 
                raise ValueError(f"{files_len} files recieved.")
            # persist report to disk 
            report_path = os.path.join(self.data_ingestion_config.REPORTS_DIR_PATH, "__load.json")
            if os.path.exists(report_path): 
                prev_data = load_json(report_path)
                prev_data[datetime.now().strftime("%H_%M_%S")] = output
                dump_json(prev_data, report_path)
                del prev_data
            else:
                dump_json({datetime.now().strftime("%H_%M_%S"):output}, report_path)
            logging.info(f"report saved at {report_path}")
            logging.info("Out __load")
            return output 
        except Exception as e: 
            logging.error(e) 
            raise CustomException(e, sys) 
        
    def __format(self, info:Dict[str, Dict[str, str]]) -> Dict[str, List[Dict[str, str]] | Dict[str, str | int]]: 
        """format data to insert into mongodb

        Args:
            info (Dict[str, Dict[str, str]]): dictionary with key as name of the file and value as another dictionary with a key named \'path\' containing path of the file

        Returns:
            
            List[Dict[str, str]]: list of json with name of file as key and base64 string as value.

            example:
            output = __format(info)
            output = {
                "info": [
                        {
                            "name":"3.pdf",
                            "data": "JVBERi0xLjcNCiW1tbW1DQoxIDAgb2Jq.......", 
                            ...
                        }
                    ]
                "schema": {
                    "path": path/of/the/file/in/disk,
                    "size": size of the file in disk,
                    "binary_content_size": total number of binary digits inside file (len(origin_data)),
                    "base64_content_size": total number of base64 digits after converting from bytes to base64 string (len(base64_data))
                }
            }
            info = output["info"]
            file_name = info[0]["name"]
            base64_string = info[0]["data"] 
        """
        try:
            logging.info("In __format") 
            output = {}
            report = {} 
            schema = {}
            for file_name in info.keys():
                logging.info(f"working with file named \'{file_name}\'")
                path = info[file_name]["path"]
                report[file_name] = {"path": path}
                schema[file_name] = {"path": path}
                try:
                    with open(path, "rb") as f:
                        content = f.read()
                    schema[file_name]["size"] = os.path.getsize(path)
                    schema[file_name]["binary_content_size"] = len(content)
                    content = bytes_to_b64str(content)
                    schema[file_name]["base64_content_size"] = len(content)
                    if isinstance(content, Exception):
                        error = deepcopy(content)
                        content = ""
                    output[file_name] = content
                    del content
                    report[file_name]["status"] = True
                except IOError as e:
                    report[file_name]["status"] = False
                    error = str(e)
                    report[file_name]["error"] = error
                    logging.error(f"error: {error}")
                del file_name, path
            # persist report to disk 
            report_path = os.path.join(self.data_ingestion_config.REPORTS_DIR_PATH, "__format.json")
            if os.path.exists(report_path): 
                prev_data = load_json(report_path)
                prev_data[datetime.now().strftime("%H_%M_%S")] = report
                dump_json(prev_data, report_path)
                del prev_data
            else:
                dump_json({datetime.now().strftime("%H_%M_%S"):report}, report_path)
            logging.info(f"report saved at {report_path}")
            # persist schema to disk 
            schema_path = os.path.join(self.data_ingestion_config.SCHEMA_DATA_DIR_PATH, "resumes.json")
            dump_json(schema, schema_path)
            logging.info(f"schema saved at {schema_path}")
            logging.info("Out __format") 
            final_output = [{"name":key, "data":value} for key, value in output.items()]
            return {
                "info": final_output, 
                "schema": schema
            }
        except Exception as e: 
            logging.error(e) 
            raise CustomException(e, sys) 
        
    def __connect(self, uri:str) -> bool:
        """tries to connects with mongodb at given uri and return status

        Args:
            uri (str): mongodb uri for connection

        Returns:
            bool: True if successful else False
        """
        try:
            self.client = pymongo.MongoClient(uri, server_api=pymongo.server_api.ServerApi('1'))
            self.database = self.client["XYZ-company"]
            self.collection = self.database["Resumes"] 

            # Send a ping to confirm a successful connection
            self.client.admin.command('ping')
            logging.info(f"connection successfull with database \'{self.database.name}\' and collection \'{self.collection.name}\'")
            return True
        except Exception as e: 
            logging.error(e)
            print(e)
            return False
            
    def __ingest(self, info:List[Dict[str, str]]) -> None: 
        """Ingest data into mongodb if the connection is successfull

        Args:
            info (List[Dict[str, str]]): list of dictionary for insertion
        """
        try:
            logging.info("In __ingest") 
            connected = self.__connect(os.getenv("MONGODB_URI"))
            if connected:
                self.collection.insert_many(info)
                logging.info("Data insertion completed")
            logging.info("Out __ingest") 
        except Exception as e: 
            logging.error(e) 
            raise CustomException(e, sys) 


    def _main(self, files: List[UploadFile]) -> Dict[str, str | int]: 
        """runs data ingestion components 

        Args:
            files (List[UploadFile]): list object of fastapi.UploadFile / files that have been uploaded

        Returns:
            Dict: shown below

            example:
            schema = _main(info)
            schema = {
                "path": path/of/the/file/in/disk,
                "size": size of the file in disk,
                "binary_content_size": total number of binary digits inside file (len(origin_data)),
                "base64_content_size": total number of base64 digits after converting from bytes to base64 string (len(base64_data))
            } 
            file_path = schema["path"]
            file_size = schema["size"]
            original_content_size = schema["binary_content_size"]
            converted_content_size = schema["base64_content_size"]
        """
        # create required dir's 
        create_dirs(self.data_ingestion_config.ROOT_DIR_PATH)
        create_dirs(self.data_ingestion_config.REPORTS_DIR_PATH)
        create_dirs(self.data_ingestion_config.SCHEMA_DATA_DIR_PATH)
        create_dirs(self.data_ingestion_config.DATA_ROOT_DIR_PATH)
        create_dirs(self.data_ingestion_config.INGESTION_ROOT_DIR_PATH)
        create_dirs(self.data_ingestion_config.RAW_DATA_DIR_PATH)
        # return back output 
        info = self.__load(files)
        output = self.__format(info)
        info = output["info"]
        schema = output["schema"]
        self.__ingest(info)
        return schema
    
__all__ = ["DataIngestionComponents"]