from abc import ABC, abstractmethod 
from src.ats import logging
from pathlib import Path


class BaseParser(ABC):
    """Base class for all document parsers"""
    
    def __init__(self):
        self.logger = logging
    
    @abstractmethod
    def parse(self, file_path: Path) -> str:
        """Parse document and return canonical representation"""
        pass
    
    @abstractmethod
    def can_handle(self, file_type: str) -> bool:
        """Check if parser can handle the given file type"""
        pass
    

__all__ = ["BaseParser", ]