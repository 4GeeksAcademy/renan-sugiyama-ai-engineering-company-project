from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .constants import TELEMETRY_ENDPOINT
from .routers.telemetry import router as telemetry_router

app = FastAPI(title="Nexova Telemetry API", version="0.1.0")
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