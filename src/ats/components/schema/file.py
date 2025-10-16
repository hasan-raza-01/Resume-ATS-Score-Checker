from dataclasses import dataclass, field
from typing import List
from pathlib import Path 


@dataclass
class FileInfo:
    path:Path = field(default=Path(""))
    parsed_path:Path = field(default=Path(""))
    structured_path: Path = field(default=Path(""))
    scores_path: Path = field(default=Path(""))
    size:int = field(default=0)
    base64_size:int = field(default=0)
    status:bool = field(default=True)
    error:List[str] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.path, str):
            self.path = Path(self.path)
        if isinstance(self.parsed_path, str):
            self.parsed_path = Path(self.parsed_path)
        if isinstance(self.structured_path, str):
            self.structured_path = Path(self.structured_path)
        if isinstance(self.scores_path, str):
            self.scores_path = Path(self.scores_path)

    # def to_dict(self) -> Dict[str, Any]:
    #     """returns dict object of class"""
    #     return {field.name: getattr(self, field.name) for field in fields(self)}


__all__ = ["FileInfo"]