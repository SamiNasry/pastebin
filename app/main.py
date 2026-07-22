from fastapi import FastAPI
from app import models

app = FastAPI()

@app.get("/")
def index():
    return{"message": "pastebin is alive"}