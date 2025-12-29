from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI(title="Time API", version="0.1.0")


@app.get("/time")
def get_server_time() -> dict[str, object]:
    """
    Returns current server time.

    - `iso`: ISO-8601 with timezone offset (server local tz).
    - `epoch_ms`: Unix timestamp in milliseconds.
    - `tz`: Server local timezone name (best-effort).
    """
    now = datetime.now(timezone.utc).astimezone()
    return {
        "iso": now.isoformat(timespec="milliseconds"),
        "epoch_ms": int(now.timestamp() * 1000),
        "tz": now.tzname(),
    }


@app.get("/date")
def get_server_date() -> dict[str, object]:
    """
    Returns current server date (server local tz).

    - `iso`: YYYY-MM-DD (server local tz).
    - `tz`: Server local timezone name (best-effort).
    """
    now = datetime.now(timezone.utc).astimezone()
    return {
        "iso": now.date().isoformat(),
        "tz": now.tzname(),
    }


@app.get("/date/utc")
def get_server_date_utc() -> dict[str, str]:
    """
    Returns current server date in UTC.
    """
    now_utc = datetime.now(timezone.utc)
    return {"iso": now_utc.date().isoformat(), "tz": "UTC"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


