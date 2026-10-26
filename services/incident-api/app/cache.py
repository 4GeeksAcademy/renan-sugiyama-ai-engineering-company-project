from __future__ import annotations

from copy import deepcopy
from threading import Lock
from time import monotonic
from typing import Generic, Hashable, TypeVar

from app.schemas import IncidentListResponse, SummaryResponse

Value = TypeVar("Value")


class TTLCache(Generic[Value]):
    def __init__(self, ttl_seconds: float, max_entries: int = 256) -> None:
        self._ttl_seconds = ttl_seconds
        self._max_entries = max_entries
        self._entries: dict[Hashable, tuple[float, Value]] = {}
        self._lock = Lock()

    def get(self, key: Hashable) -> Value | None:
        now = monotonic()
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if expires_at <= now:
                del self._entries[key]
                return None
            return deepcopy(value)

    def set(self, key: Hashable, value: Value) -> None:
        now = monotonic()
        with self._lock:
            expired_keys = [
                entry_key
                for entry_key, (expires_at, _) in self._entries.items()
                if expires_at <= now
            ]
            for entry_key in expired_keys:
                del self._entries[entry_key]

            if key not in self._entries and len(self._entries) >= self._max_entries:
                oldest_key = min(
                    self._entries,
                    key=lambda entry_key: self._entries[entry_key][0],
                )
                del self._entries[oldest_key]
            self._entries[key] = (now + self._ttl_seconds, deepcopy(value))

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()


incident_list_cache: TTLCache[IncidentListResponse] = TTLCache(ttl_seconds=10)
incident_summary_cache: TTLCache[SummaryResponse] = TTLCache(
    ttl_seconds=5,
    max_entries=1,
)


def clear_incident_caches() -> None:
    incident_list_cache.clear()
    incident_summary_cache.clear()