from fastapi import FastAPI

from app.routers import health, pessoas

app = FastAPI(
    title="SAFE API",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(pessoas.router)