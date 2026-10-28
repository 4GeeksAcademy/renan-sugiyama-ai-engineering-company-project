import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from psycopg_pool import ConnectionPool

from .constants import TELEMETRY_ENDPOINT
from .routers.telemetry import router as telemetry_router


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    database_url = os.getenv("TELEMETRY_DATABASE_URL")
    if not database_url:
        raise RuntimeError("TELEMETRY_DATABASE_URL must be configured")

    pool = ConnectionPool(database_url, min_size=1, max_size=5, open=False)
    try:
        pool.open(wait=True)
        application.state.telemetry_pool = pool
        yield
    finally:
        pool.close()


app = FastAPI(title="Nexova Telemetry API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)
app.state.telemetry_endpoint = TELEMETRY_ENDPOINT
app.include_router(telemetry_router)