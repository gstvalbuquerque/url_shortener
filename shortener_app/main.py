from fastapi import FastAPI

from .core.models import models
from .core.models.database import engine
from .routers import shortener


app = FastAPI()
models.Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return "Welcome to the URL shortener API :)"


app.include_router(shortener.router)
