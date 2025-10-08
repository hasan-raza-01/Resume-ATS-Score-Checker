from .scorers import *
from .. import logging
from ..entity import Scoring
from ..components.schema import *
from ..exception import CustomException
from ..utils import awrite_json
from typing import Dict
from pathlib import Path, PurePath
from copy import deepcopy
from datetime import datetime
import sys, asyncio, aiofiles, json


class ScoringComponents:
    def __init__(self, config:Scoring, resume_data:Dict[str, ResumeSchema], job_data:JobDescription, info:Dict[str, FileInfo]) -> None:
        self.__config = config
        self.__resume_data = resume_data
        self.__jd = job_data
        self.__info = info
        self.__scores = {}

    def __await__(self):
        return self.__main().__await__()
    
    async def __score(self):
        scoring_tasks = []
        scoring_True_files = []
        try:
            scorer = ResumeScorer()
            for name in self.__info:
                info = self.__info.get(name)
                resume_data = self.__resume_data[name]
                if info.status:
                    scoring_tasks.append(asyncio.create_task(scorer.score(resume_data, self.__jd)))
                    scoring_True_files.append(name)
            # wait for scorings 
            scores = await asyncio.gather(*scoring_tasks, return_exceptions=True)
            # update info and append scores to instance variable with respect to file name and create save tasks
            save_tasks = []
            save_True_files = []
            for name, score in list(zip(scoring_True_files, scores)):
                info = self.__info.get(name)
                if isinstance(score, Exception):
                    info.status = False
                    info.error.append(score)
                if info.status:
                    self.__scores[name] = score
                    # create task 
                    path = self.__config.SCORING_DATA_DIR_PATH.joinpath(Path(name).stem + Path(name).suffix.replace(".", "_")).with_suffix(".json").absolute()
                    if not path.parent.exists():
                        path.mkdir(parents=True, exist_ok=True)
                    save_tasks.append(asyncio.create_task(awrite_json(path, score)))
                    save_True_files.append(name)
                self.__info[name] = info 
            # wait for i/o operation completion
            results = await asyncio.gather(*save_tasks, return_exceptions=True)
            # update info
            for name, res in list(zip(save_True_files, results)):
                info = self.__info.get(name)
                if isinstance(res, Exception):
                    info.status = False
                    info.error.append(res)
                if info.status:
                    path = self.__config.SCORING_DATA_DIR_PATH.joinpath(Path(name).stem + Path(name).suffix.replace(".", "_")).with_suffix(".json").absolute()
                    info.scores_path = path
                self.__info[name] = info
        except Exception as e:
            e = CustomException(e, sys)
            logging.error(e)
    
    async def __main(self) -> tuple[Dict[str, FileInfo], Dict[str, Dict]]:
        """returns a dict for calculated scores with recommendation, key = file name, value = dict of scores and other info
        """
        logging.info("In Scoring")
        if self.__resume_data and self.__jd:
            # get scores and persist it to disk 
            await self.__score()
            # save info 
            errors = []
            i = 1
            data = {}
            for key in self.__info:
                try:
                    info = deepcopy(self.__info[key])
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
                timestamp = self.__config.TIME_STAMP.strftime("%d_%m_%Y_%H_%M_%S")
                path = self.__config.OUTPUT_DIR_PATH.joinpath(f"{timestamp}.json")
                if not path.parent.exists():
                    path.parent.mkdir(parents=True, exist_ok=True)
                if path.exists():
                    self.__config.TIME_STAMP = datetime.now()
                    timestamp = self.__config.TIME_STAMP.strftime("%d_%m_%Y_%H_%M_%S")
                    path = self.__config.OUTPUT_DIR_PATH.joinpath(f"{timestamp}.json")
                # persist data to directory 
                await awrite_json(path, data)
                logging.info(f"info saved at \'{path.as_posix()}\'")
            except Exception as e:
                e = CustomException(e, sys)
                errors.append("\t"*10+str(i)+") "+str(e))
            if errors:
                logging.error(f"error occured while persisting final data to disk, errors: \n{"\n".join(errors)}")
                print("Scoring Errors")
                print("-------------------------")
                for error in errors:
                    print(error)
            logging.info("Out Scoring")
            return (self.__info, self.__scores)
    
__all__ = ["ScoringComponents"]