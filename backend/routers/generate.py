from fastapi import APIRouter
from pydantic import BaseModel
from utils.generator import generate_image

router = APIRouter()

class GenerateRequest(BaseModel):
    prompt: str
    negative_prompt: str = ""
    width: int = 512
    height: int = 512
    num_outputs: int = 1

@router.post("/generate")
async def generate(req: GenerateRequest):
    results = generate_image(
        prompt=req.prompt,
        negative_prompt=req.negative_prompt,
        width=req.width,
        height=req.height,
        num_outputs=req.num_outputs
    )
    return {"images": results}  # 파일명 리스트 반환
