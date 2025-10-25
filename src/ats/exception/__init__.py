import sys as SYS
from src.ats import logging


class CustomException(Exception):

    def __init__(self, message:str | Exception, sys:SYS):
        self.message = message
        super().__init__(message)
        _, _, exc_traceback = sys.exc_info()
        self.path = exc_traceback.tb_frame.f_code.co_filename
        self.line = exc_traceback.tb_lineno

    def __str__(self):
        return f"CustomException: {self.message} on line: {self.line} of {self.path}"

class BaseError(Exception):
    
    def __init__(self, rec:str, exp: str) -> None:
        if not isinstance(rec, str):
            raise TypeError(f"required \'{str}\' but recieved \'{type(rec)}\'")
        if not isinstance(exp, str):
            raise TypeError(f"required \'{str}\' but recieved \'{type(exp)}\'")
        self.rec = rec 
        self.exp = exp
        super().__init__(self.rec, self.exp)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: expected \'{self.exp}\' but recieved \'{self.rec}\'"
    
    
class FileTypeError(BaseError):
    "error for unknown file type"
    pass

class MinFileSizeError(BaseError):
    "error for minimal file size"
    pass

class MinContextError(BaseError):
    "error for minimal context inside file"
    pass

class ResumeTokenLimitError(Exception):
    "error for resume token limit"
    pass 

__all__ = ["CustomException", "FileTypeError", "MinFileSizeError", "MinContextError", "ResumeTokenLimitError"]

if __name__=="__main__":
    try:
        1/0
    except Exception as e:
        logging.exception(e)
        raise CustomException(e, SYS)

