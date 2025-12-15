from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def list_search():
    return {"message": "search endpoint - implementation ready"}
