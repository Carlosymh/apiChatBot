from fastapi import FastAPI
from src.api.endpoints import router

app = FastAPI(title="Chat Bot API", version="1.0.0")

app.include_router(router)
