from fastapi import FastAPI
from app.api import router

app = FastAPI(title="GenAI Research Assistant")

app.include_router(router)
