
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api import router

app = FastAPI(title="GenAI Research Assistant")

# Mount the static directory to serve files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(router)
