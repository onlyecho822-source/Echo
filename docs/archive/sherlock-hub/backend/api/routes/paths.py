from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def list_paths():
    return {"message": "paths endpoint - implementation ready"}
