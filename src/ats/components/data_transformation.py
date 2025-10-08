from dotenv import load_dotenv 
load_dotenv()

from ..exception import CustomException, ResumeTokenLimitError
from ..entity import DataTransformation, DataIngestion
from ..components.parsers.base import BaseParser
from ..utils import asave_file, awrite_json
from ..components.parsers import *
from ..components.schema import *
from .. import logging
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pathlib import PurePath, Path
from datetime import datetime
from typing import Dict, Any
from copy import deepcopy
import os, sys, asyncio, aiofiles, json
 

class DataTransformationComponents:
    def __init__(self ,config: DataTransformation, ing_config: DataIngestion, data: Dict[str, FileInfo] | None = None, llm:BaseChatModel | None = None) -> None:
        """if data is None, DataIngesion artifacts must be available before initializing, otherwise error will be raised
        if llm is None, llm = ChatGoogleGenerativeAI, make sure to have required environment variables"""
        self.__stop_execution = False
        if not isinstance(config, DataTransformation):
            self.__stop_execution = True
            raise TypeError(f"\'config\' must be an instance of \'{DataTransformation}\'")
        if not isinstance(ing_config, DataIngestion):
            self.__stop_execution = True
            raise TypeError(f"\'ing_config\' must be an instance of \'{DataIngestion}\'")
        if data:
            if not isinstance(data, dict):
                self.__stop_execution = True
                raise TypeError(f"\'data\' must be a \'{dict}\'")
            for k in data:
                if not isinstance(data[k], FileInfo):
                    self.__stop_execution = True
                    raise TypeError(f"\'data\' must be a {dict} of file name as keys and value as a instances of \'{FileInfo}\' not \'{type(data[k])}\'")
        self.__data = data
        self.__config = config
        self.__ing_config = ing_config
        self.__llm = llm
        self.__parsers = {
            ".pdf": PDFParser,
            ".docx": DOCXParser,
            ".html" :HTMLParser,
            "jd": JobDescriptionParser
        }
        self.__parsers_args = {
            ".pdf": {},
            ".docx": {},
            ".html" :{},
            "jd": {}
        }
        if not self.__llm:
            if not os.getenv("GOOGLE_API_KEY"):
                raise EnvironmentError("no environment variable \'GOOGLE_API_KEY\'")
            self.__llm = ChatGoogleGenerativeAI(model=os.getenv("LLM", "gemini-2.5-pro"))
            logging.info(f"using \'{self.__llm.model}\' as LargeLanguageModel")
        self.__parsed_data = {}
        self.__structured_data = {}
        self.__train_data = None
    
    @property 
    def parsers(self) -> Dict[str, object]:
        return self.__parsers
    
    @property
    def parsers_args(self) -> Dict[str, Dict[str, Any]]:
        return self.__parsers_args
    
    def __await__(self):
        return self.__main().__await__()
    
    async def __load_data_from_disk(self) -> tuple[bool, None | Exception]:
        try:
            err = None
            timestamp = self.__ing_config.TIME_STAMP.strftime("%d_%m_%Y_%H_%M_%S")
            path = self.__ing_config.OUTPUT_DIR_PATH.joinpath(f"{timestamp}.json")
            if not path.is_file():
                raise FileNotFoundError(f"not found {path.as_posix()}")
            async with aiofiles.open(path, encoding="utf-8", newline="\n") as f:
                content = await f.read()
            self.__data = {name: FileInfo(**info) for name, info in json.loads(content).items()}
            res = True
            logging.info("\'info\' loaded from disk.")
        except Exception as e:
            err = e
            res = False
        return res, err

    def extend_parsers(self, v:Dict[str, object], update:bool = False, params:dict[str, any] = None) -> Dict[str, object]:
        """adds parser to the private attribute having all parsers

        Args:
            v (Dict[str, object]): suffix/extension as key, un-initialized object of parser args as value
                eg: 
                v = {
                    '.txt': PARSER_CLASS
                }
            update (bool, optional): set it to True if you want to update existing key in private attribute having all parsers. Defaults to False.
            params (dict[str, any], optional): params to initialize parser. Defaults to None.
            
            Note: 
                -  parser must be inherited from \'BaseParser\' import statement --> from src.ats.components.parsers.base import BaseParser
                -  parser object must have a awaitable method named \'parse(coroutine)\' runs whole parsing process,
                -  parser will only be pickedup to run method parse with a keyword argument \'path\', path --> path/to/the/file.pdf
                -  args of parser should be given as kwargs while will be used to intialize the parser object
                -  parser must return a single string value of the parsed data, usage of parser shown below
                    
                    example: 
                    parser_class = parsers['.txt']
                    parser = parser_class(**params)
                    output = await parser.parse(path='path/to/file')

        Raises:
            ValueError: if arg 'v' is not an object of dict
            ValueError: if trying to add more than one parser at a time
            ValueError: if parser object is not an instance of \'BaseParser\'
            KeyError: if arg 'update' is set to False and and key in v already exists in private attribute having all parsers

        Returns:
            Dict[str, object]: private attribute having all parsers, suffix/extension as key, un-initialized object of parser as value
        """
        try:
            if not isinstance(v, dict):
                raise ValueError(f"arg \'v\' should belongs to \'{dict}\' object, but recieved {type(v)}") 
            if len(v) > 1:
                raise ValueError(f"one parser can be added at a time")
            if not update:
                for suffix, parser in v.items():
                    if not isinstance(parser, BaseParser):
                        raise ValueError(f"\'{parser.__class__.__name__}\' must be inherited from \'BaseParser\'")
                    if suffix in self.__parsers:
                        raise KeyError(f"arg \'update\' is set to {update} and trying to update the existing key \'{suffix}\'")
            if not params:
                params = {}
            suffix = list(v.keys())[0]
            self.__parsers_args.update({suffix: params})
            self.__parsers.update(v)
            return self.__parsers
        except Exception as e:
            raise CustomException(e, sys)

    async def __parse(self) -> None: 
        "parse the staged data"
        if self.__stop_execution:
            logging.critical(f"__stop_execution={self.__stop_execution}, stoping execution. from __parse")
            return
        logging.info("In __parse")
        try:
            # parse the data 
            parse_tasks = []
            parse_True_files = []
            for name in self.__data:
                info = self.__data.get(name)
                if info.status:
                    path = info.path
                    suffix = path.suffix.strip().lower()
                    # get parser 
                    try:
                        if suffix not in self.__parsers:
                            raise KeyError(f"no parser have been added for \'{suffix}\' files")
                        else:
                            parser_class = self.__parsers[suffix]
                            args = self.__parsers_args[suffix]
                            parser = parser_class(**args)
                            parse_tasks.append(asyncio.create_task(parser.parse(path=path)))
                            parse_True_files.append(path.name)
                    except Exception as e:
                        info.status = False
                        e = CustomException(e, sys)
                        info.error.append(str(e))
                        logging.critical(str(e) + f" name={name}")
                    self.__data[name] = info
                else:
                    logging.critical(f"file-status={info.status}, skipping file \'{name}\'")
            parsed_output = await asyncio.gather(*parse_tasks, return_exceptions=True)
            # save the files 
            save_tasks = []
            save_True_files = []
            for name, parsed_data in list(zip(parse_True_files, parsed_output)):
                # add data to private instance variable 
                self.__parsed_data[name] = parsed_data
                # opearation 
                info = self.__data.get(name)
                if info.status:
                    if isinstance(parsed_data, Exception):
                        info.status = False
                        parsed_data = CustomException(parsed_data, sys)
                        info.error.append(str(parsed_data))
                        logging.critical(str(parsed_data) + f" name={name}")
                    else:
                        parsed_path = self.__config.PARSED_DATA_DIR_PATH.joinpath(name)
                        save_tasks.append(asyncio.create_task(asave_file(parsed_data, parsed_path)))
                        save_True_files.append(name)
                    self.__data[name] = info
                else:
                    logging.critical(f"file-status={info.status}, skipping file \'{name}\'")
            save_tasks_ouptut = await asyncio.gather(*save_tasks, return_exceptions=True)
            # update parsed path of file
            for name, output in list(zip(save_True_files, save_tasks_ouptut)):
                info = self.__data.get(name)
                if info.status:
                    if isinstance(output, Exception):
                        info.status = False
                        output = CustomException(output, sys)
                        info.error.append(str(output))
                        logging.critical(str(output) + f" name={name}")
                    else:
                        info.parsed_path = output
                    self.__data[name] = info
                else:
                    logging.critical(f"file-status={info.status}, skipping file \'{name}\'")
        except Exception as e:
            logging.error(str(CustomException(e, sys)))
            self.__stop_execution = True
        logging.info("Out __parse")
        
    async def __extract_keyword(self) -> None: 
        "extract structed output from parsed string data"
        if self.__stop_execution:
            logging.critical(f"__stop_execution={self.__stop_execution}, stoping execution. from __extract_keyword")
            return
        if not self.__parsed_data:
            logging.critical(f"no parsed data available")
            return
        logging.info("In __extract_keyword")
        try:
            train_data = {
                "X":[], 
                "y":[]
            }
            structured_llm = self.__llm.with_structured_output(ResumeSchema)
            prompt_message = self.__config.PROMPT
            prompt_template = ChatPromptTemplate.from_template(prompt_message)
            token_limit = int(os.getenv("RESUME_TOKEN_LIMIT"))
            # get prompts
            prompt_tasks = []
            prompt_True_files = []
            for name in self.__data:
                parsed_data = self.__parsed_data[name]
                info = self.__data.get(name)
                if info.status:
                    if parsed_data:
                        prompt_tasks.append(asyncio.create_task(prompt_template.ainvoke({"input_data": parsed_data})))
                        prompt_True_files.append(name)
                    else:
                        info.status = False
                        parsed_data = CustomException(parsed_data, sys)
                        info.error.append(f"no parsed data, len={len(parsed_data)}")
                        logging.critical(str(parsed_data) + f" name={name}")
                    self.__data[name] = info
                else:
                    logging.critical(f"file-status={info.status}, skipping file \'{name}\'")
            prompts = await asyncio.gather(*prompt_tasks, return_exceptions=True)
            # create structured output tasks
            structured_tasks = []
            structured_True_files = []
            for name, prompt in list(zip(prompt_True_files, prompts)):
                parsed_data = self.__parsed_data[name]
                info = self.__data.get(name)
                if info.status:
                    try:
                        if isinstance(prompt, Exception):
                            raise prompt
                        if len(parsed_data.split()) > token_limit:
                            raise ResumeTokenLimitError(f"Please use a consize resume, your current resume have {len(parsed_data.split())} tokens, limit: {token_limit}")
                        structured_tasks.append(asyncio.create_task(structured_llm.ainvoke(prompt)))
                        structured_True_files.append(name)
                    except Exception as e:
                        info.status = False
                        e = CustomException(e, sys)
                        info.error.append(str(e))
                        logging.critical(str(e) + f", name={name}")
                    self.__data[name] = info
                else:
                    logging.critical(f"file-status={info.status}, skipping file \'{name}\'")
            # wait to collect all output
            structured_outputs = await asyncio.gather(*structured_tasks, return_exceptions=True)
            # create save tasks 
            save_tasks = []
            save_True_files = []
            for name, structured_data in list(zip(structured_True_files, structured_outputs)):
                info = self.__data.get(name)
                parsed_data = self.__parsed_data[name]
                if info.status:
                    try:
                        if isinstance(structured_data, Exception):
                            raise structured_data
                        # add to training data
                        train_data["X"].append(parsed_data)
                        train_data["y"].append(structured_data.model_dump())
                        # add data to private instance variable
                        self.__structured_data[name] = structured_data
                        path = self.__config.STRUCTURED_DATA_DIR_PATH.joinpath(Path(name).stem + Path(name).suffix.replace(".", "_")).with_suffix(".json").absolute()
                        if not path.parent.is_dir():
                            path.parent.mkdir(parents=True, exist_ok=True)
                        # create task 
                        save_tasks.append(asyncio.create_task(awrite_json(path, structured_data.model_dump())))
                        save_True_files.append(name)
                    except Exception as e:
                        info.status = False
                        e = CustomException(e, sys)
                        info.error.append(str(e))
                        logging.critical(str(e) + f", name=\'{name}\'")
                    self.__data[name] = info
                else:
                    logging.critical(f"file-status={info.status}, skipping file \'{name}\'")
            self.__train_data = train_data
            # collect results 
            results = await asyncio.gather(*save_tasks, return_exceptions=True)
            # update info
            for name, result in list(zip(save_True_files, results)):
                info = self.__data.get(name)
                if info.status:
                    if isinstance(result, Exception):
                        info.status = False
                        info.error.append(str(result))
                        logging.critical(str(result) + f", name={name}")
                    else:
                        info.structured_path = self.__config.STRUCTURED_DATA_DIR_PATH.joinpath(Path(name).stem + Path(name).suffix.replace(".", "_")).with_suffix(".json").absolute()
                    self.__data[name] = info
                else:
                    logging.critical(f"file-status={info.status}, skipping file \'{name}\'")
        except Exception as e:
            logging.error(str(CustomException(e, sys)))
            self.__stop_execution = True
        logging.info("Out __extract_keyword")
        
    async def __main(self) -> tuple[Dict[str, ResumeSchema], Dict[str, FileInfo]]:
        "runs the transformation pipeline and returns structured data and all files information"
        logging.info("In DataTransformation")
        errors = []
        i = 1
        # read data from disk if not provided while initialization
        if self.__data is None:
            res, e = await self.__load_data_from_disk()
            if not res:
                self.__stop_execution = True
                e = CustomException(e, sys)
                logging.error(str(e))
                print(e)
        await self.__parse()
        await self.__extract_keyword()
        # save train data
        timestamp = self.__config.TIME_STAMP.strftime("%d_%m_%Y_%H_%M_%S")
        try:
            if not self.__train_data is None:
                self.__config.TIME_STAMP = datetime.now()
                train_data_path = self.__config.TRAIN_DATA_DIR_PATH.joinpath(f"{timestamp}.json")
                if not train_data_path.exists():
                    train_data_path.parent.mkdir(parents=True, exist_ok=True)
                # persist 
                await awrite_json(train_data_path, self.__train_data)
                logging.info(f"train data saved at \'{train_data_path.as_posix()}\'")
            else:
                logging.warning(f"no training data are available to save")
        except Exception as e:
            e = CustomException(e, sys)
            errors.append("\t"*10+str(i)+") "+str(e))
        # save info 
        data = {}
        for key in self.__data:
            try:
                info = deepcopy(self.__data[key])
                if isinstance(info.path, PurePath):
                    info.path = info.path.as_posix()
                    info.parsed_path = info.parsed_path.as_posix()
                    info.structured_path = info.structured_path.as_posix()
                    info.scores_path = info.scores_path.as_posix()
                data[key] = vars(info)
            except Exception as e:
                e = CustomException(e, sys)
                errors.append("\t"*10+str(i)+") "+str(e))
                i += 1
        try:
            path = self.__config.OUTPUT_DIR_PATH.joinpath(f"{timestamp}.json")
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            # persist 
            await awrite_json(path, data)
            logging.info(f"info saved at \'{path.as_posix()}\'")
        except Exception as e:
            e = CustomException(e, sys)
            errors.append("\t"*10+str(i)+") "+str(e))
        if errors:
            logging.error(f"error occured while persisting final data to disk, errors: \n{"\n".join(errors)}")
            print("DataTransformation Errors")
            print("-------------------------")
            for error in errors:
                print(error)
        logging.info("Out DataTransformation")
        return (self.__structured_data, self.__data)
        
__all__ = ["DataTransformationComponents"]