from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/")
def health_check():
    return JSONResponse({"message": "GenAI API is working!"})
