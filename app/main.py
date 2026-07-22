from fastapi import FastAPI
from app import models
from app.routes import api

app = FastAPI(title="pastebin")

app.include_router(api.router)


@app.get("/health")
def health():
    return{"status": "ok"}