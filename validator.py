"""Row validation: airport list loading, single-row checks, record building."""

import math
import re
from datetime import datetime


FLIGHT_ID_RE = re.compile(r"^[A-Za-z0-9]{2,8}$")
AIRPORT_RE = re.compile(r"^[A-Z]{3}$")
DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")


def load_airports(path: str) -> set[str]:
    """Read an airport list file and return the set of codes."""
    airports = set()

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            code = line.strip()

            if not code or code.startswith("#"):
                continue

            airports.add(code)

    return airports


def _parse_datetime_exact(value: str) -> datetime | None:
    if not DATETIME_RE.fullmatch(value):
        return None

    try:
        parsed = datetime.strptime(value, "%Y-%m-%d %H:%M")
    except ValueError:
        return None

    return parsed


def validate_row(fields: list[str], airports: set[str]) -> str | None:
    """Return the first validation error code, or None if valid."""

    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    values = [field.strip() for field in fields]

    if any(value == "" for value in values):
        return "MISSING_FIELD"

    flight_id, origin, destination, departure, arrival, price_text = values

    if not FLIGHT_ID_RE.fullmatch(flight_id):
        return "INVALID_FLIGHT_ID"

    if not AIRPORT_RE.fullmatch(origin) or origin not in airports:
        return "INVALID_ORIGIN"

    if not AIRPORT_RE.fullmatch(destination) or destination not in airports:
        return "INVALID_DESTINATION"

    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"

    departure_dt = _parse_datetime_exact(departure)
    if departure_dt is None:
        return "INVALID_DEPARTURE"

    arrival_dt = _parse_datetime_exact(arrival)
    if arrival_dt is None:
        return "INVALID_ARRIVAL"

    if arrival_dt <= departure_dt:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    try:
        price = float(price_text)
    except ValueError:
        return "INVALID_PRICE"

    if not math.isfinite(price):
        return "INVALID_PRICE"

    if price <= 0:
        return "NON_POSITIVE_PRICE"

    return None


def to_record(fields: list[str]) -> dict:
    """Turn a valid row into a flight record dictionary."""
    values = [field.strip() for field in fields]

    return {
        "flight_id": values[0],
        "origin": values[1],
        "destination": values[2],
        "departure_datetime": values[3],
        "arrival_datetime": values[4],
        "price": float(values[5]),
    }