import certifi
ca = certifi.where() 

from fastapi import FastAPI, UploadFile, File, Response 
from fastapi.middleware.cors import CORSMiddleware 
from src.ats.pipeline import * 
from datetime import datetime 
from typing import List 
import uvicorn 


app = FastAPI(
    title="Resume Checker [ATS]",
    description="AI powered Resume Checker",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # set specific origins in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# health check 
@app.get("/health", tags=["health"])
async def health_check():
    return Response(
        content="Running.....",
        status_code=200,
        headers={
            "status": "ok",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
    )

# upload resume 
@app.post("/upload")
async def upload(files:List[UploadFile] = File(...)):
    try:
        ingestion_pipeline = DataIngestionPipeline()
        ingestion_pipeline._run(files)
        return Response("upload successfully completed.")
    except Exception as e:
        print(e)
        return Response(str(e), 500)


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000) 


