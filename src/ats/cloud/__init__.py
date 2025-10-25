from google.cloud.storage import Client, transfer_manager
from google.oauth2 import service_account
from ..exception import CustomException
from abc import ABC, abstractmethod
from pathlib import Path
from .. import logging
import sys, os, asyncio


class BaseCloud(ABC):
    def __init__(self):
        self.credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not self.credentials_path:
            raise EnvironmentError(f"Env var \'GOOGLE_APPLICATION_CREDENTIALS\' having value \'{self.credentials_path}\'")

    def verify_args(self):
        # Load credentials from file
        credentials = service_account.Credentials.from_service_account_file(self.credentials_path)
        self.client = Client(credentials=credentials)
        self.bucket = self.client.bucket(self.bucket_name)
        if not isinstance(self.src, Path):
            self.src = Path(self.src)
        if not isinstance(self.dst, Path):
            self.dst = Path(self.dst)
    
    def enter(self):
        logging.info(f"entered {self.__class__.__name__}.")
    
    def exit(self):
        logging.info(f"{self.__class__.__name__} exited.")
    
    @ abstractmethod
    def upload(self):
        pass

    @ abstractmethod
    def download(self):
        pass

class GCPFileManager(BaseCloud):
    def verify_args(self):
        return super().verify_args()
    
    def __enter(self):
        return super().enter()
    
    def __exit(self):
        return super().exit()

    async def upload(self, bucket:str, src:Path | str, dst:Path | str) -> bool:
        loop = asyncio.get_running_loop()
        def func():
            self.__enter()
            self.bucket_name = bucket
            self.src = src
            self.dst = dst
            self.verify_args()
            status = True
            try:
                # Create a blob (object) and upload the file
                blob = self.bucket.blob(str(self.dst))
                # upload
                blob.upload_from_filename(str(self.src))
                logging.info(f"File uploaded to {blob.name}")
            except Exception as e:
                logging.error(str(CustomException(e, sys)))
                status = False
            self.__exit()
            return status
        return await loop.run_in_executor(None, func)
    
    async def download(self, bucket:str, src:Path | str, dst:Path | str) -> bool:
        loop = asyncio.get_running_loop()
        def func():
            self.__enter()
            self.bucket_name = bucket
            self.src = src
            self.dst = dst
            self.verify_args()
            status = True
            try:
                # Create a blob (object) and upload the file
                blob = self.bucket.blob(str(self.src))
                # Download to local file
                blob.download_to_filename(str(self.dst))
                logging.info(f"File downloaded to {str(self.dst)}")
            except Exception as e:
                logging.error(str(CustomException(e, sys)))
                status = False
            self.__exit()
            return status
        return await loop.run_in_executor(None, func)

class GCPFolderManager(BaseCloud):
    def verify_args(self):
        return super().verify_args()
    
    def __enter(self):
        return super().enter()
    
    def __exit(self):
        return super().exit()

    async def upload(self, bucket:str, src:Path | str, dst:Path | str, workers:int = 8) -> bool:
        loop = asyncio.get_running_loop()
        def func():
            self.__enter()
            self.bucket_name = bucket
            self.src = src
            self.dst = dst
            self.verify_args()
            status = True
            try:
                paths = self.src.rglob("*")

                # Filter to include only files, not directories
                file_paths = [path for path in paths if path.is_file()]
                
                source_directory = str(self.src)
                # Make paths relative to source_directory to preserve structure
                relative_paths = [path.relative_to(source_directory) for path in file_paths]
                
                # Convert to strings
                string_paths = [str(path) for path in relative_paths]
                
                logging.info(f"Found {len(string_paths)} files to upload.")
                
                # **KEY FIX**: Prepend the destination folder prefix to each path
                # If self.dst is something like 'logs', prepend it
                if hasattr(self, 'dst') and self.dst:
                    # Ensure dst is treated as a folder prefix
                    dst_prefix = str(self.dst).strip('/')
                    blob_names = [f"{dst_prefix}/{path}" for path in string_paths]
                else:
                    blob_names = string_paths
                
                # Upload all files with their directory structure preserved
                results = transfer_manager.upload_many_from_filenames(
                    self.bucket, 
                    string_paths,  # Local file paths (relative)
                    source_directory=source_directory,
                    blob_name_prefix=f"{dst_prefix}/",  # Add prefix for destination
                    max_workers=workers
                )
                
                # Check results
                for name, result in zip(blob_names, results):
                    if isinstance(result, Exception):
                        logging.info(f"Failed to upload {name}: {result}")
                        status = False
                    else:
                        logging.info(f"Uploaded {name} to {self.bucket.name}")
            except Exception as e:
                logging.error(str(CustomException(e, sys)))
                status = False
            self.__exit()
            return status
        return await loop.run_in_executor(None, func)
    
    async def download(self, bucket:str, src:Path | str, dst:Path | str) -> bool:
        loop = asyncio.get_running_loop()
        def func():
            self.__enter()
            self.bucket_name = bucket
            self.src = src
            self.dst = dst
            self.verify_args()
            status = True
            try:
                # **KEY FIX**: Use proper prefix for the folder
                # If self.src is 'logs', this will list all blobs under 'logs/'
                prefix = str(self.src).strip('/') + '/'
                blobs = self.bucket.list_blobs(prefix=prefix)

                downloaded_count = 0
        
                for blob in blobs:
                    # Skip if it's a folder marker (ends with /)
                    if blob.name.endswith('/'):
                        continue
                    
                    # Remove the prefix to get relative path
                    relative_name = blob.name[len(prefix):]
                        
                    # Create the full local path, preserving directory structure
                    local_path = self.dst.joinpath(relative_name)
                    
                    # Create nested directories if they don't exist
                    if local_path.suffix:  # if file then only create parent directories
                        local_path.parent.mkdir(parents=True, exist_ok=True)
                    else:  # if directory then create full path
                        local_path.mkdir(parents=True, exist_ok=True)
                        
                    # Download the file
                    blob.download_to_filename(str(local_path))
                    logging.info(f"Downloaded {blob.name} to {str(local_path)}")
                    downloaded_count += 1
                
                logging.info(f"\nTotal files downloaded: {downloaded_count}")
            except Exception as e:
                logging.error(str(CustomException(e, sys)))
                status = False
            self.__exit()
            return status
        return await loop.run_in_executor(None, func)


__all__ = ["GCPFileManager", "GCPFolderManager"]