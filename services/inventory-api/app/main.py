from __future__ import annotations

from fastapi import FastAPI

from app.db import initialize_database
from app.routers import inventory_items

app = FastAPI(title="Nexova Inventory API", version="0.1.0")
app.include_router(inventory_items.router)


@app.on_event("startup")
def startup() -> None:
    initialize_database()
