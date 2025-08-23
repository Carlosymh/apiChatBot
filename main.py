from fastapi import FastAPI
from src.api.endpoints import router

app = FastAPI("Chat Bot API")

app.include_router(router)
