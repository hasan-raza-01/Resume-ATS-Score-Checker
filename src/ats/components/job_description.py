from .schema import JobDescription as JobDescriptionSchema
from .parsers import JobDescriptionParser
from ..exception import CustomException 
from .. import logging 
from ..entity import *
import os, sys, json, aiofiles


class JobDescriptionComponents:
    def __init__(self, config:JobDescription, url:str = None):
        self.__config = config 
        self.url = url 

        if not self.url:
            if not os.getenv("JD_URL"):
                raise EnvironmentError("environment variable \'JD_URL\' not found")
            self.url = os.getenv("JD_URL")

    def __await__(self):
        return self.__main().__await__()

    async def __main(self) -> JobDescriptionSchema:
        logging.info("In JobDescription")
        try:
            parser = JobDescriptionParser()
            job_description = await parser.parse(self.url)
            if job_description:
                # persist data to disk
                timestamp = self.__config.TIME_STAMP.strftime("%d_%m_%Y_%H_%M_%S")
                path = self.__config.JD_ROOT_DIR_PATH.joinpath(f"{timestamp}.json")
                if not path.parent.exists():
                    path.parent.mkdir(parents=True, exist_ok=True)
                payload = json.dumps(job_description.model_dump(), ensure_ascii=False, indent=2)
                async with aiofiles.open(path, "w", encoding="utf-8", newline="\n") as f:
                        await f.write(payload)
                logging.info(f"job description saved at \'{path.as_posix()}\'")
                return job_description
            else:
                raise ValueError(f"job_description is having type \'{type(job_description)}\'")
        except Exception as e:
            e = CustomException(e, sys)
            logging.error(f"error occured while persisting final data to disk, errors: \n{e}")
        logging.info("Out JobDescription")

__all__ = ["JobDescriptionComponents"]
