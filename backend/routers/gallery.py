from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter()

RESULT_DIR = "results"

@router.get("/results")
async def list_results():
    files = os.listdir(RESULT_DIR)
    return {"images": files}

@router.get("/results/{filename}")
async def get_image(filename: str):
    filepath = os.path.join(RESULT_DIR, filename)
    return FileResponse(filepath)
