# update __all__ also inside __init__ 

from .parsers import *
from src.ats.utils import save_file, create_dirs
from src.ats.exception import CustomException 
from dataclasses import dataclass 
from src.ats import logging 
from fastapi import UploadFile 
from string import punctuation 
from src.ats.entity import * 
from pathlib import Path 
from typing import Dict, List 
import sys, os 


@dataclass
class DataIngestionComponents: 
    data_ingestion_config: DataIngestion 

    def __load(self, files:List[UploadFile]) -> Dict[str, Path]: 
        """loads data, stores locally and returns name with path

        Args:
            files (List[UploadFile]): list object of fastapi.UploadFile / files that have been uploaded

        Raises:
            ValueError: if no files have been provided as argument

        Returns:
            Dict:
            key = name of file 

            value = path of file 

            example:
            output = __load(files)
            output = {
                "xyz.pdf" : "path\\to\\the\\file", 
                "abc.docx": "path\\to\\the\\file", 
                ...
            } 
            name = output.keys()[0]
            path = output[name]
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
                    # save file to local 
                    ext = os.path.splitext(file_name)[-1].lower()
                    if ext == ".pdf" or ext == ".docx" or ext == ".html":
                        save_file(file.file, path) 
                    else:
                        save_file(file.file.read(), path)
                    del ext
                    logging.info(f"stagged \'{file_name}\'")
                    output[file_name] = path 
            else: 
                raise ValueError(f"{files_len} files recieved.")
            logging.info("Out __load")
            return output 
        except Exception as e: 
            logging.error(e) 
            raise CustomException(e, sys) 
        
    def __parse(self, info:Dict[str, Path]) -> Dict[str, str]: 
        """parse the data of file through unstructured, supported extentions ---> [ .pdf, .docx, .html ]

        Args:
            info (Dict[str, Path]): 

                key = name of file 

                value = path of file 

                example:
                info = {
                    "xyz.pdf" : "path\\to\\the\\file", 
                    "abc.docx": "path\\to\\the\\file", 
                    ...
                } 
                output = __parse(info)

        Raises:
            ValueError: if provided file with uncompatable format as argument 

        Returns:
            Dict: 
            key = name of file 

            value = string object of parsed data  

            example:
            output = __parse(info)
            output = {
                "xyz.pdf" : "string_parsed_data_of_xyz.pdf", 
                "abc.docx": "string_parsed_data_of_abc.docx", 
                ...
            } 
            name = output.keys()[0]
            data = output[name] 
        """
        try:
            logging.info("In __parse")
            output = {}
            for file_name in info.keys():
                logging.info(f"parsing \'{file_name}\'")
                ext = os.path.splitext(file_name)[1].lower()
                # get parser 
                if ext == ".pdf":
                    parser = PDFParser()
                elif ext == ".docx":
                    parser = DOCXParser()
                elif ext == ".html":
                    parser = HTMLParser()
                else:
                    raise ValueError(f"Unsupported file type: {file_name}") 
                logging.info(f"using \'{parser.__class__.__name__}\'")
                path = info[file_name]
                logging.info(f"path of file for parsing \'{path}\'") 
                extracted_data = parser.parse(path)
                del parser
                logging.info("parsing complete.")
                # save file to local 
                path = os.path.join(self.data_ingestion_config.PARSED_DATA_DIR_PATH, file_name)
                save_file(extracted_data, path) 
                logging.info(f"parsed \'{file_name}\'")
                del path, ext 
                output[file_name] = extracted_data 
                del extracted_data 
            logging.info("Out __parse") 
            return output 
        except Exception as e: 
            logging.error(e) 
            raise CustomException(e, sys) 
        
    # def __clean(self, info:Dict[str, str]) -> Dict[str, str]: 
    #     """removes punctuations from parsed data 

    #     Args:
    #         info (Dict[str, str]): 
            
    #             key = name of file 

    #             value = string object of parsed data  

    #             example:
    #             info = {
    #                 "xyz.pdf" : "string_parsed_data_of_xyz.pdf", 
    #                 "abc.docx": "string_parsed_data_of_abc.docx", 
    #                 ...
    #             } 
    #             output = __clean(info)

    #     Returns:
    #         Dict: 
    #         key = name of file 

    #         value = cleaned string object of parsed data  

    #         example:
    #         output = __clean(info)
    #         output = {
    #             "xyz.pdf" : "cleaned_string_parsed_data_of_xyz.pdf", 
    #             "abc.docx": "cleaned_string_parsed_data_of_abc.docx", 
    #             ...
    #         } 
    #         name = output.keys()[0]
    #         data = output[name] 
    #     """
    #     try:
    #         logging.info("In __clean") 
    #         output = {} 
    #         for file_name in info.keys():
    #             logging.info(f"cleaning \'{file_name}\'")
    #             new_line_char = " mmmmmmm " 
    #             elements_string = info[file_name]
    #             elements_string = elements_string.replace("\n", new_line_char)
    #             # elements_string = re.sub(r'–', '-', elements_string) 
    #             for i in punctuation+'–': 
    #                 elements_string = elements_string.replace(i, " ") 
    #             elements_string = " ".join(elements_string.split())
    #             elements_string = elements_string.replace(new_line_char.strip(), "\n") 
    #             del new_line_char 
    #             # save file to local 
    #             path = os.path.join(self.data_ingestion_config.FINAL_DATA_DIR_PATH, file_name)
    #             save_file(elements_string, path) 
    #             logging.info(f"cleaned parsed content of \'{file_name}\'")
    #             output[file_name] = elements_string 
    #             del elements_string 
    #         logging.info("Out __clean") 
    #         return output
    #     except Exception as e: 
    #         logging.error(e) 
    #         raise CustomException(e, sys) 

    def _main(self, files: List[UploadFile]) -> Dict[str, str]: 
        """runs data ingestion components 

        Args:
            files (List[UploadFile]): list object of fastapi.UploadFile / files that have been uploaded

        Returns:
            Dict: 
            key = name of file 

            value = cleaned string object of parsed data  

            example:
            output = _main(info)
            output = {
                "xyz.pdf" : "cleaned_string_parsed_data_of_xyz.pdf", 
                "abc.docx": "cleaned_string_parsed_data_of_abc.docx", 
                ...
            } 
            name = output.keys()[0]
            data = output[name] 
        """
        # create required dir's 
        create_dirs(self.data_ingestion_config.ROOT_DIR_PATH)
        create_dirs(self.data_ingestion_config.DATA_ROOT_DIR_PATH)
        create_dirs(self.data_ingestion_config.INGESTION_ROOT_DIR_PATH)
        create_dirs(self.data_ingestion_config.RAW_DATA_DIR_PATH)
        create_dirs(self.data_ingestion_config.PARSED_DATA_DIR_PATH)
        # create_dirs(self.data_ingestion_config.FINAL_DATA_DIR_PATH)
        # return the final output 
        # return self.__clean(self.__parse(self.__load(files)))
        return self.__parse(self.__load(files))
    
__all__ = ["DataIngestionComponents"]