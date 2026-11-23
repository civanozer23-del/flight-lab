"""Query handling for flight records."""

import re
from datetime import datetime


DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")

RECORD_KEYS = {
    "flight_id",
    "origin",
    "destination",
    "departure_datetime",
    "arrival_datetime",
    "price",
}

ALLOWED_KEYS = RECORD_KEYS | {
    "min_price",
    "sort_by",
    "order",
    "limit",
}


def _valid_datetime(value: str) -> bool:
    if not isinstance(value, str):
        return False

    if not DATETIME_RE.fullmatch(value):
        return False

    try:
        datetime.strptime(value, "%Y-%m-%d %H:%M")
    except ValueError:
        return False

    return True


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _valid_query(query: dict) -> bool:
    if not isinstance(query, dict):
        return False

    if any(key not in ALLOWED_KEYS for key in query):
        return False

    for key in ("flight_id", "origin", "destination"):
        if key in query and not isinstance(query[key], str):
            return False

    for key in ("departure_datetime", "arrival_datetime"):
        if key in query and not _valid_datetime(query[key]):
            return False

    for key in ("price", "min_price"):
        if key in query and not _is_number(query[key]):
            return False

    if "sort_by" in query:
        if query["sort_by"] not in RECORD_KEYS:
            return False

    if "order" in query:
        if query["order"] not in ("asc", "desc"):
            return False

        if "sort_by" not in query:
            return False

    if "limit" in query:
        limit = query["limit"]

        if not isinstance(limit, int) or isinstance(limit, bool):
            return False

        if limit < 0:
            return False

    return True


def run_query(db: list[dict], query: dict) -> dict:
    """Run one query and return its response entry."""

    if not _valid_query(query):
        return {
            "query": query,
            "error": "INVALID_QUERY",
            "matches": [],
        }

    matches = []

    for flight in db:
        if "flight_id" in query and flight["flight_id"] != query["flight_id"]:
            continue

        if "origin" in query and flight["origin"] != query["origin"]:
            continue

        if (
            "destination" in query
            and flight["destination"] != query["destination"]
        ):
            continue

        if (
            "departure_datetime" in query
            and flight["departure_datetime"] < query["departure_datetime"]
        ):
            continue

        if (
            "arrival_datetime" in query
            and flight["arrival_datetime"] > query["arrival_datetime"]
        ):
            continue

        if "price" in query and flight["price"] > query["price"]:
            continue

        if "min_price" in query and flight["price"] < query["min_price"]:
            continue

        matches.append(flight)

    if "sort_by" in query:
        reverse = query.get("order", "asc") == "desc"

        matches = sorted(
            matches,
            key=lambda flight: flight[query["sort_by"]],
            reverse=reverse,
        )

    if "limit" in query:
        matches = matches[: query["limit"]]

    return {
        "query": query,
        "matches": matches,
    }


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Run one query object or a list of query objects."""

    if isinstance(queries, dict):
        queries = [queries]

    return [run_query(db, query) for query in queries]