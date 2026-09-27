from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import initialize_database
from app.routers import inventory_items, inventory_movements

app = FastAPI(title="Nexova Inventory API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "X-Inventory-User"],
)
app.include_router(inventory_items.router)
app.include_router(inventory_movements.router)


@app.on_event("startup")
def startup() -> None:
    initialize_database()
