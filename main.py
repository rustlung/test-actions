from __future__ import annotations

from datetime import datetime, timezone

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import FastAPI, HTTPException, Query

app = FastAPI(title="Time API", version="0.1.0")

CITY_TZ_ALIASES: dict[str, str] = {
    # RU
    "москва": "Europe/Moscow",
    "moscow": "Europe/Moscow",
    "спб": "Europe/Moscow",
    "питер": "Europe/Moscow",
    "санкт_петербург": "Europe/Moscow",
    "saint_petersburg": "Europe/Moscow",
    "yekaterinburg": "Asia/Yekaterinburg",
    "екатеринбург": "Asia/Yekaterinburg",
    "novosibirsk": "Asia/Novosibirsk",
    "новосибирск": "Asia/Novosibirsk",
    "vladivostok": "Asia/Vladivostok",
    "владивосток": "Asia/Vladivostok",
    # World
    "london": "Europe/London",
    "париж": "Europe/Paris",
    "paris": "Europe/Paris",
    "berlin": "Europe/Berlin",
    "tokyo": "Asia/Tokyo",
    "sydney": "Australia/Sydney",
    "dubai": "Asia/Dubai",
    "singapore": "Asia/Singapore",
    "hong_kong": "Asia/Hong_Kong",
    "bangkok": "Asia/Bangkok",
    "delhi": "Asia/Kolkata",
    "new_york": "America/New_York",
    "los_angeles": "America/Los_Angeles",
    "chicago": "America/Chicago",
}


def _normalize_city(value: str) -> str:
    return (
        value.strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace(",", "")
    )


def _resolve_tz(city_or_tz: str) -> tuple[ZoneInfo, str]:
    raw = city_or_tz.strip()
    key = _normalize_city(raw)

    tz_name = CITY_TZ_ALIASES.get(key)
    if tz_name is None and "/" in raw:
        tz_name = raw
    if tz_name is None:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "unknown_city_or_timezone",
                "message": "Unknown city. Provide a supported city alias (e.g. 'Moscow', 'London') or an IANA timezone like 'Europe/Moscow'.",
                "city": raw,
                "examples": ["Moscow", "London", "New_York", "Europe/Moscow", "America/New_York"],
            },
        )

    try:
        return ZoneInfo(tz_name), tz_name
    except ZoneInfoNotFoundError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "timezone_not_found",
                "message": "Timezone was resolved but not found on this system. Ensure tzdata is installed.",
                "timezone": tz_name,
            },
        ) from e


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


@app.get("/time/convert")
def get_time_in_timezone(
    city: str = Query(
        ...,
        description="City name (e.g. Moscow, London, New_York) or an IANA timezone (e.g. Europe/Moscow).",
        min_length=1,
    ),
) -> dict[str, object]:
    """
    Returns current time converted to the requested timezone.
    """
    tz, tz_name = _resolve_tz(city)
    now = datetime.now(timezone.utc).astimezone(tz)
    return {
        "requested": city,
        "iso": now.isoformat(timespec="milliseconds"),
        "epoch_ms": int(now.timestamp() * 1000),
        "tz": tz_name,
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


