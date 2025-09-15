import logging
logging.basicConfig(level=logging.INFO)

from fastapi import FastAPI
from app.api import providers, ask

app = FastAPI()

app.include_router(providers.router)

