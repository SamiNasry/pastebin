from fastapi import FastAPI
from app import models
from app.routes import api, pages


app = FastAPI(title="pastebin")

app.include_router(api.router)
app.include_router(pages.router)


@app.get("/health")
def health():
    return{"status": "ok"}