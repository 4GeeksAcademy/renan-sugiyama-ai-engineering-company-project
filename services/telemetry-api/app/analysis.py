"""Pandas analysis pipeline for technical telemetry reports."""

from collections.abc import Sequence
from datetime import datetime
from typing import Any

import pandas as pd
from psycopg_pool import ConnectionPool

OPERATIONAL_EVENT_TYPES = (
    "support_ticket_resolved",
    "support_queue_snapshot_recorded",
    "support_query_closed",
    "support_dissatisfaction_detected",
    "support_ticket_escalated",
    "user_authentication_denied",
    "stock_movement_validation_failed",
    "direct_stock_edit_rejected",
    "outbound_stock_blocked",
    "stock_movement_recorded",
    "stock_threshold_triggered",
    "stock_movement_correction_recorded",
    "api_latency_recorded",
    "api_request_failed",
)

_EVENTS_PER_DAY_QUERY = """
    SELECT timestamp, event_type
    FROM public.telemetry_events
    WHERE timestamp >= %s AND timestamp < %s
      AND event_type = ANY(%s)
"""

_API_LATENCY_QUERY = """
    SELECT timestamp, tags
    FROM public.telemetry_events
    WHERE timestamp >= %s AND timestamp < %s
      AND event_type = %s
"""

_LATENCY_TAG_COLUMNS = ["routeTemplate", "method", "httpStatus", "durationMs"]


def _read_frame(
    pool: ConnectionPool,
    query: str,
    parameters: Sequence[Any],
    columns: Sequence[str],
) -> pd.DataFrame:
    with pool.connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, parameters)
            rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=columns)


def _add_utc_date(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True, errors="coerce")
    frame = frame.dropna(subset=["timestamp"]).copy()
    frame["date"] = frame["timestamp"].dt.strftime("%Y-%m-%d")
    return frame


def _load_api_latency(
    start_date: datetime,
    end_date: datetime,
    pool: ConnectionPool,
) -> pd.DataFrame:
    frame = _read_frame(
        pool,
        _API_LATENCY_QUERY,
        (start_date, end_date, "api_latency_recorded"),
        ("timestamp", "tags"),
    )
    frame = _add_utc_date(frame)
    tag_frame = pd.json_normalize(frame.pop("tags")).reindex(
        columns=_LATENCY_TAG_COLUMNS
    )
    frame = frame.join(tag_frame)

    frame = frame.dropna(subset=["routeTemplate", "method"]).copy()
    frame["routeTemplate"] = frame["routeTemplate"].astype("string").str.strip()
    frame["method"] = frame["method"].astype("string").str.strip().str.upper()
    has_dimensions = frame["routeTemplate"].ne("") & frame["method"].ne("")
    frame = frame.loc[has_dimensions].copy()

    status = pd.to_numeric(frame["httpStatus"], errors="coerce")
    valid_status = status.between(100, 599) & status.mod(1).eq(0)
    frame = frame.loc[valid_status].copy()
    frame["httpStatus"] = status.loc[valid_status].astype("int64")
    return frame


def events_per_day(
    start_date: datetime,
    end_date: datetime,
    pool: ConnectionPool,
) -> list[dict[str, Any]]:
    frame = _read_frame(
        pool,
        _EVENTS_PER_DAY_QUERY,
        (start_date, end_date, list(OPERATIONAL_EVENT_TYPES)),
        ("timestamp", "event_type"),
    )
    frame = _add_utc_date(frame)
    if frame.empty:
        return []

    result = (
        frame.groupby(["date", "event_type"])
        .agg(count=("event_type", "count"))
        .reset_index()
    )
    return result.to_dict(orient="records")


def error_rate_by_type(
    start_date: datetime,
    end_date: datetime,
    pool: ConnectionPool,
) -> list[dict[str, Any]]:
    frame = _load_api_latency(start_date, end_date, pool)
    if frame.empty:
        return []

    frame["request_type"] = frame["method"].str.cat(frame["routeTemplate"], sep=" ")
    frame["is_server_error"] = frame["httpStatus"].ge(500)
    result = (
        frame.groupby(["date", "request_type"])
        .agg(
            request_count=("is_server_error", "count"),
            server_error_count=("is_server_error", "sum"),
        )
        .reset_index()
    )
    result["error_rate"] = result["server_error_count"] / result["request_count"]
    return result.to_dict(orient="records")


def average_latency_by_endpoint(
    start_date: datetime,
    end_date: datetime,
    pool: ConnectionPool,
) -> list[dict[str, Any]]:
    frame = _load_api_latency(start_date, end_date, pool)
    if frame.empty:
        return []

    duration = pd.to_numeric(frame["durationMs"], errors="coerce")
    valid_duration = (
        duration.notna()
        & duration.ge(0)
        & duration.ne(float("inf"))
        & duration.ne(float("-inf"))
    )
    frame = frame.loc[valid_duration].copy()
    frame["durationMs"] = duration.loc[valid_duration]
    if frame.empty:
        return []

    result = (
        frame.groupby(["date", "routeTemplate", "method"])
        .agg(
            sample_count=("durationMs", "count"),
            average_latency_ms=("durationMs", "mean"),
        )
        .reset_index()
    )
    return result.to_dict(orient="records")