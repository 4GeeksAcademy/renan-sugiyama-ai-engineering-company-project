from datetime import datetime as DateTime
from datetime import timezone
from importlib import import_module
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from psycopg import OperationalError

telemetry = import_module("app.routers.telemetry")

METRICS = {
    "events_per_day": [{"event_type": "api_request_failed", "count": 1}],
    "error_rate_by_type": [{"request_type": "GET /items", "error_rate": 0.1}],
    "average_latency_by_endpoint": [
        {"routeTemplate": "/items", "method": "GET", "average_latency_ms": 12.5}
    ],
}


class FrozenDateTime(DateTime):
    @classmethod
    def now(cls, tz: Any = None) -> "FrozenDateTime":
        return cls(2026, 10, 30, 12, 34, 56, tzinfo=tz or timezone.utc)


@pytest.fixture(name="report_client")
def _provide_report_client() -> Any:
    application = FastAPI()
    application.include_router(telemetry.router)
    application.state.telemetry_pool = object()
    _reset_report_cache()
    with TestClient(application) as test_client:
        yield test_client, application
    _reset_report_cache()


def _reset_report_cache() -> None:
    cache_lock = getattr(telemetry, "_REPORT_CACHE_LOCK")
    report_cache = getattr(telemetry, "_REPORT_CACHE")
    with cache_lock:
        report_cache.clear()


def test_report_defaults_to_seven_days_and_returns_expected_shape(
    report_client: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    test_client, application = report_client
    calls: list[tuple[DateTime, DateTime, Any]] = []
    monkeypatch.setattr(telemetry, "datetime", FrozenDateTime)
    monkeypatch.setattr(
        telemetry,
        "build_telemetry_report",
        lambda start, end, pool: calls.append((start, end, pool)) or METRICS,
    )

    response = test_client.get("/telemetry/report")

    assert response.status_code == 200
    assert response.json() == {
        "period": {"from": "2026-10-23T12:34:00Z", "to": "2026-10-30T12:34:00Z"},
        "metrics": METRICS,
    }
    assert calls == [
        (
            DateTime(2026, 10, 23, 12, 34, tzinfo=timezone.utc),
            DateTime(2026, 10, 30, 12, 34, tzinfo=timezone.utc),
            application.state.telemetry_pool,
        )
    ]


@pytest.mark.parametrize(
    ("params", "expected_start", "expected_end"),
    [
        (
            {
                "start_date": "2026-10-29T10:00:00-04:00",
                "end_date": "2026-10-30T10:00:00+02:00",
            },
            "2026-10-29T14:00:00Z",
            "2026-10-30T08:00:00Z",
        ),
        (
            {"start_date": "2026-10-29T10:00:00-04:00"},
            "2026-10-29T14:00:00Z",
            "2026-10-30T12:34:00Z",
        ),
        (
            {"end_date": "2026-10-30T10:00:00+02:00"},
            "2026-10-23T08:00:00Z",
            "2026-10-30T08:00:00Z",
        ),
    ],
)
def test_report_normalizes_supplied_and_one_sided_bounds(
    report_client: Any,
    monkeypatch: pytest.MonkeyPatch,
    params: dict[str, str],
    expected_start: str,
    expected_end: str,
) -> None:
    test_client, _ = report_client
    monkeypatch.setattr(telemetry, "datetime", FrozenDateTime)
    monkeypatch.setattr(telemetry, "build_telemetry_report", lambda *_: METRICS)

    response = test_client.get("/telemetry/report", params=params)

    assert response.status_code == 200
    assert response.json()["period"] == {"from": expected_start, "to": expected_end}


@pytest.mark.parametrize(
    "params",
    [
        {"start_date": "2026-10-29T10:00:00"},
        {"start_date": "not-a-date"},
        {
            "start_date": "2026-10-30T10:00:00Z",
            "end_date": "2026-10-30T10:00:00Z",
        },
        {
            "start_date": "2026-10-31T10:00:00Z",
            "end_date": "2026-10-30T10:00:00Z",
        },
    ],
)
def test_report_rejects_naive_invalid_or_empty_periods(
    report_client: Any,
    params: dict[str, str],
) -> None:
    test_client, _ = report_client

    response = test_client.get("/telemetry/report", params=params)

    assert response.status_code == 422


def test_report_returns_503_without_database_pool(report_client: Any) -> None:
    test_client, application = report_client
    application.state.telemetry_pool = None

    response = test_client.get("/telemetry/report")

    assert response.status_code == 503
    assert response.json()["detail"] == "Telemetry report database unavailable"


def test_report_returns_sanitized_503_for_database_errors(
    report_client: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    test_client, _ = report_client

    def raise_database_error(*args: Any) -> dict[str, Any]:
        raise OperationalError("sensitive connection detail")

    monkeypatch.setattr(telemetry, "build_telemetry_report", raise_database_error)

    response = test_client.get(
        "/telemetry/report",
        params={
            "start_date": "2026-10-29T00:00:00Z",
            "end_date": "2026-10-30T00:00:00Z",
        },
    )

    assert response.status_code == 503
    assert "sensitive" not in response.text


def test_report_cache_hits_for_normalized_window_and_expires(
    report_client: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    test_client, _ = report_client
    calls: list[tuple[DateTime, DateTime]] = []
    clock = [100.0]
    monkeypatch.setattr(telemetry, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        telemetry,
        "build_telemetry_report",
        lambda start, end, pool: calls.append((start, end)) or METRICS,
    )
    utc_params = {
        "start_date": "2026-10-29T00:00:00Z",
        "end_date": "2026-10-30T00:00:00Z",
    }
    offset_params = {
        "start_date": "2026-10-28T20:00:00-04:00",
        "end_date": "2026-10-29T20:00:00-04:00",
    }

    first = test_client.get("/telemetry/report", params=utc_params)
    second = test_client.get("/telemetry/report", params=offset_params)
    assert first.json() == second.json()
    assert len(calls) == 1

    different_window = test_client.get(
        "/telemetry/report",
        params={
            "start_date": "2026-10-28T00:00:00Z",
            "end_date": "2026-10-29T00:00:00Z",
        },
    )
    assert different_window.status_code == 200
    assert len(calls) == 2

    clock[0] += telemetry.REPORT_CACHE_TTL_SECONDS + 1
    expired = test_client.get("/telemetry/report", params=utc_params)
    assert expired.status_code == 200
    assert len(calls) == 3


def test_default_window_cache_key_is_stable_within_a_minute(
    report_client: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    test_client, _ = report_client
    calls: list[tuple[DateTime, DateTime]] = []
    monkeypatch.setattr(telemetry, "datetime", FrozenDateTime)
    monkeypatch.setattr(
        telemetry,
        "build_telemetry_report",
        lambda start, end, pool: calls.append((start, end)) or METRICS,
    )

    first = test_client.get("/telemetry/report")
    second = test_client.get("/telemetry/report")

    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    assert len(calls) == 1