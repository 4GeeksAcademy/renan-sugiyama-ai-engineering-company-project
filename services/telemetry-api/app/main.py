from fastapi import FastAPI

from .constants import TELEMETRY_ENDPOINT
from .routers.telemetry import router as telemetry_router

app = FastAPI(title="Nexova Telemetry API", version="0.1.0")
app.state.telemetry_endpoint = TELEMETRY_ENDPOINT
app.include_router(telemetry_router)