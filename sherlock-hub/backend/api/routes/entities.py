from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def list_entities():
    return {"message": "entities endpoint - implementation ready"}
