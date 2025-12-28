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


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


