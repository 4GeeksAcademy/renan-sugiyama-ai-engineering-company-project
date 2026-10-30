import json
from datetime import datetime, timezone
from typing import Any

from app.analysis import (
    OPERATIONAL_EVENT_TYPES,
    average_latency_by_endpoint,
    error_rate_by_type,
    events_per_day,
)

START = datetime(2026, 6, 1, tzinfo=timezone.utc)
END = datetime(2026, 6, 3, tzinfo=timezone.utc)


class FakeCursor:
    def __init__(self, pool: "FakePool") -> None:
        self.pool = pool
        self.rows: list[tuple[Any, ...]] = []
        self.query = ""

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, *args: Any) -> None:
        return None

    def execute(self, query: str, parameters: tuple[Any, ...]) -> None:
        self.query = query
        self.pool.calls.append((query, parameters))
        self.rows = (
            self.pool.event_rows if "ANY(%s)" in query else self.pool.latency_rows
        )

    def fetchall(self) -> list[tuple[Any, ...]]:
        return self.rows


class FakeConnection:
    def __init__(self, pool: "FakePool") -> None:
        self.pool = pool

    def __enter__(self) -> "FakeConnection":
        return self

    def __exit__(self, *args: Any) -> None:
        return None

    def cursor(self) -> FakeCursor:
        return FakeCursor(self.pool)


class FakePool:
    def __init__(
        self,
        event_rows: list[tuple[Any, ...]] | None = None,
        latency_rows: list[tuple[Any, ...]] | None = None,
    ) -> None:
        self.event_rows = event_rows or []
        self.latency_rows = latency_rows or []
        self.calls: list[tuple[str, tuple[Any, ...]]] = []

    def connection(self) -> FakeConnection:
        return FakeConnection(self)


def assert_sql_window_and_event_type(
    pool: FakePool,
    expected_event_type: str | list[str],
) -> None:
    assert len(pool.calls) == 1
    query, parameters = pool.calls[0]
    assert "timestamp >= %s AND timestamp < %s" in query
    assert "event_type =" in query
    assert parameters[:2] == (START, END)
    assert parameters[2] == expected_event_type


def test_events_per_day_filters_in_sql_and_groups_by_utc_date() -> None:
    pool = FakePool(
        event_rows=[
            ("2026-06-01T00:15:00-02:00", "api_request_failed"),
            ("2026-05-31T23:30:00-02:00", "api_request_failed"),
            ("2026-06-02T01:00:00+02:00", "support_ticket_resolved"),
            ("2026-06-02T00:30:00Z", "api_request_failed"),
        ]
    )

    result = events_per_day(START, END, pool)

    assert result == [
        {"date": "2026-06-01", "event_type": "api_request_failed", "count": 2},
        {
            "date": "2026-06-01",
            "event_type": "support_ticket_resolved",
            "count": 1,
        },
        {"date": "2026-06-02", "event_type": "api_request_failed", "count": 1},
    ]
    assert_sql_window_and_event_type(pool, list(OPERATIONAL_EVENT_TYPES))
    json.dumps(result)


def test_error_rate_uses_valid_status_rows_and_groups_by_request_type() -> None:
    pool = FakePool(
        latency_rows=[
            (
                "2026-06-01T23:15:00-02:00",
                {
                    "routeTemplate": "/items",
                    "method": "get",
                    "httpStatus": 500,
                    "durationMs": 25,
                },
            ),
            (
                "2026-06-02T01:30:00Z",
                {
                    "routeTemplate": "/items",
                    "method": "GET",
                    "httpStatus": 200,
                    "durationMs": 10,
                },
            ),
            (
                "2026-06-02T02:00:00Z",
                {
                    "routeTemplate": "/items",
                    "method": "POST",
                    "httpStatus": 599,
                    "durationMs": 10,
                },
            ),
            (
                "2026-06-02T02:10:00Z",
                {
                    "routeTemplate": "/items",
                    "method": "POST",
                    "httpStatus": 400,
                    "durationMs": 10,
                },
            ),
            (
                "2026-06-02T02:20:00Z",
                {
                    "routeTemplate": "/items",
                    "method": "POST",
                    "httpStatus": 599.5,
                    "durationMs": 10,
                },
            ),
            ("2026-06-02T02:30:00Z", None),
        ]
    )

    result = error_rate_by_type(START, END, pool)

    assert result == [
        {
            "date": "2026-06-02",
            "request_type": "GET /items",
            "request_count": 2,
            "server_error_count": 1,
            "error_rate": 0.5,
        },
        {
            "date": "2026-06-02",
            "request_type": "POST /items",
            "request_count": 2,
            "server_error_count": 1,
            "error_rate": 0.5,
        },
    ]
    assert_sql_window_and_event_type(pool, "api_latency_recorded")
    json.dumps(result)


def test_average_latency_discards_invalid_rows_and_reports_sample_count() -> None:
    pool = FakePool(
        latency_rows=[
            (
                "2026-06-01T23:15:00-02:00",
                {
                    "routeTemplate": "/items",
                    "method": "get",
                    "httpStatus": 200,
                    "durationMs": 10,
                },
            ),
            (
                "2026-06-02T02:00:00Z",
                {
                    "routeTemplate": "/items",
                    "method": "GET",
                    "httpStatus": 500,
                    "durationMs": 20,
                },
            ),
            (
                "2026-06-02T02:10:00Z",
                {
                    "routeTemplate": "/items",
                    "method": "GET",
                    "httpStatus": 200,
                    "durationMs": -1,
                },
            ),
            (
                "2026-06-02T02:20:00Z",
                {
                    "routeTemplate": "/items",
                    "method": "GET",
                    "httpStatus": 200,
                    "durationMs": float("inf"),
                },
            ),
            (
                "2026-06-02T02:30:00Z",
                {
                    "routeTemplate": "/items",
                    "method": "GET",
                    "httpStatus": 99,
                    "durationMs": 100,
                },
            ),
            (
                "2026-06-02T02:40:00Z",
                {"method": "GET", "httpStatus": 200, "durationMs": 30},
            ),
            (
                "2026-06-02T02:50:00Z",
                {
                    "routeTemplate": "/items",
                    "httpStatus": 200,
                    "durationMs": 30,
                },
            ),
        ]
    )

    result = average_latency_by_endpoint(START, END, pool)

    assert result == [
        {
            "date": "2026-06-02",
            "routeTemplate": "/items",
            "method": "GET",
            "sample_count": 2,
            "average_latency_ms": 15.0,
        }
    ]
    assert_sql_window_and_event_type(pool, "api_latency_recorded")
    json.dumps(result)


def test_metrics_return_serializable_empty_lists() -> None:
    pool = FakePool()

    results = [
        events_per_day(START, END, pool),
        error_rate_by_type(START, END, pool),
        average_latency_by_endpoint(START, END, pool),
    ]

    assert results == [[], [], []]
    json.dumps(results)