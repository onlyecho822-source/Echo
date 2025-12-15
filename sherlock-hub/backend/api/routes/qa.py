from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def list_qa():
    return {"message": "qa endpoint - implementation ready"}
