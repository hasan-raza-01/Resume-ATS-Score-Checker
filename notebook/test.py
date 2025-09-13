# import asyncio
# import time
# from pathlib import Path
# from src.ats.utils import asave_file

# paths = []
# for path in Path("artifacts/data/ingestion/raw").iterdir():
#     paths.append(path.absolute())
# for path in Path("artifacts/data/transformation/parsed").iterdir():
#     paths.append(path.absolute())
# info = {}
# for path in paths:
#     with open(path, "rb") as f:
#         info[f.read()] = Path(path)
# print(len(info))

# async def main():
#     tasks = []
#     for content, path in info.items():
#         tasks.append(asyncio.create_task(asave_file(content, path)))
#     return await asyncio.gather(*tasks, return_exceptions=True)


# if __name__ == "__main__":
#     start = time.time()
#     results = asyncio.run(main())
#     print("Execution time", time.time()-start)
#     print("\nResult:-")
#     for result in results:
#         print(result)

import asyncio, time

async def func(): 
    await asyncio.sleep(0)
    print("Hii")

st = time.time()
asyncio.run(func())
async_taken = time.time() - st

def func():
    print("Hii")

st = time.time()
func()
normal_taken = time.time() - st  

print(async_taken - normal_taken)
