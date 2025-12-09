from fastapi import APIRouter



router = APIRouter(prefix="/storage", tags=["Storage"])


@router.get("/")
async def hello():
    return {
        "Hello" : "World"
        }