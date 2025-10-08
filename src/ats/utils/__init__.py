from pathlib import Path
from src.ats.exception import CustomException
import re, aiofiles, sys, json

async def asave_file(content:str | bytes, path:Path) -> Path | Exception: 
    """saves content into file at given path

    Args:
        content (str | bytes): string content of to write inside file or bytes
        path (Path): destination path for content to be saved

    Raises:
        TypeError: incorrect type for \'content\'
        TypeError: incorrect type for \'path\'
        ValueError: if \'path\' do not ends with a suffix

    Returns:
        str | Exception: updated file name or exception occured while performing operation
    """
    try:
        # type validation
        # ------------------
        # content
        if isinstance(content, str):
            mode = "wt"
        elif isinstance(content, bytes):
            mode = "wb"
        else:
            raise TypeError(f"arg \'content\' need \'{str}\'/\'{bytes}\' got \'{type(content)}\'")
        # path
        if not isinstance(path, Path):
            raise TypeError(f"arg \'path\' need \'{Path}\' got \'{type(path)}\'")
        # get absolute path if path is not absolute
        if not path.is_absolute():
            path = path.absolute()
        # raise error if path does not ends with a file
        if not path.suffix:
            raise ValueError(f"\'path\' must end with a file with extention.\n\tlike:- path/to/the/directory/file.txt\n\tcurrent path:- {path.as_posix()}")
        # create path if not available 
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        # extract vars
        suffix = path.suffix.strip().lower()
        # check does wheather data is string and not saving original(bytes) data recieve from user
        if isinstance(content, str) and "raw" not in path.as_posix():
            suffix = suffix.replace(".", "_") + ".txt"
        # update path if extenstion has been changed
        if suffix != path.suffix.strip().lower():
            path = path.with_stem(path.stem + Path(suffix).stem).with_suffix(Path(suffix).suffix)
        # get unique name for file
        available_files = [e.name for e in path.parent.iterdir() if e.suffix]
        while True:
            if not path.exists() and path.name not in available_files:
                break
            else: 
                match_result = re.search(r'\(([1-9]\d*)\)', path.stem.strip().lower())
                if not match_result:
                    path = path.with_stem(path.stem + "(1)") 
                else:
                    element = match_result.group(1) 
                    start, end = len(path.stem)-(len(element)+2), len(path.stem)
                    name = path.stem[:path.stem.index(element, start, end)-1] + f"({int(element) + 1})" + suffix
                    path = path.with_name(name)
        async with aiofiles.open(path, mode) as file:
            await file.write(content)
        return path
    except Exception as e:
        raise CustomException(e, sys)

async def awrite_json(path:Path, data:dict):
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    async with aiofiles.open(path, "w", encoding="utf-8", newline="\n") as f:
        await f.write(payload)
