from ..exception import CustomException 
from ..entity import CloudPush
from .. import logging 
from ..cloud import *
import sys, os


class CloudPushComponents:
    def __init__(self, config:CloudPush):
        self.config = config

    def __await__(self):
        return self.__main().__await__()
    
    async def __main(self):
        """pushes file and folder from src(local) to dst(cloud)
        """
        logging.info("In CloudPushComponents")
        try:
            cloud_file_manager = GCPFileManager()
            cloud_folder_manager = GCPFolderManager()
            if self.config.FILES:
                logging.info(f"recieved {len(self.config.FILES)} files to push to cloud")
                for src, dst in self.config.FILES.items():
                    res = await cloud_file_manager.upload(
                        bucket=os.getenv("GCP_BUCKET"), 
                        src=src, 
                        dst=dst
                        )
                    if isinstance(res, Exception):
                        try:
                            res = CustomException(res, sys)
                        except:
                            pass
                        logging.error(res)

            if self.config.FOLDERS:
                logging.info(f"recieved {len(self.config.FOLDERS)} folders to push to cloud")
                for src, dst in self.config.FOLDERS.items():
                    res = await cloud_folder_manager.upload(
                        bucket=os.getenv("GCP_BUCKET"), 
                        src=src, 
                        dst=dst
                        )
                    if isinstance(res, Exception):
                        try:
                            res = CustomException(res, sys)
                        except:
                            pass
                        logging.error(res)

        except Exception as e:
            try:
                e = CustomException(e, sys)
            except:
                pass
            logging.error(e)
        logging.info("Out CloudPushComponents")
