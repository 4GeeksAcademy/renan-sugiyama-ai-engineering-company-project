from __future__ import annotations

import os
from pathlib import Path

DATABASE_PATH = Path(
    os.getenv(
        "INVENTORY_DATABASE_PATH",
        Path(__file__).parent.parent / "data" / "inventory.db",
    )
)

INVENTORY_UNITS = ("unit", "pack", "box", "ream", "roll", "liter", "kg")
DEFAULT_INVENTORY_UNIT = "unit"
