"""Reading CSV files into flight records and error messages."""

import csv
import os

from validator import validate_row, to_record


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Process CSV files in the given order and return records and errors."""

    records = []
    errors = []

    # Only previously accepted valid flights count for duplicate checking.
    seen_flights = set()

    for path in paths:
        file_name = os.path.basename(path)

        with open(path, "r", encoding="utf-8", newline="") as file:
            for line_number, raw_line in enumerate(file, start=1):

                # Line 1 is always the header.
                if line_number == 1:
                    continue

                # Blank lines and comment lines still count in line numbering,
                # but they are not validated or logged.
                if not raw_line.strip():
                    continue

                if raw_line.lstrip().startswith("#"):
                    continue

                fields = next(csv.reader([raw_line]))

                error_code = validate_row(fields, airports)

                if error_code is not None:
                    original = raw_line.rstrip("\r\n")
                    errors.append(
                        f"{file_name}:{line_number}: {error_code} | {original}"
                    )
                    continue

                stripped_fields = [field.strip() for field in fields]

                duplicate_key = (
                    stripped_fields[0],
                    stripped_fields[3],
                )

                if duplicate_key in seen_flights:
                    original = raw_line.rstrip("\r\n")
                    errors.append(
                        f"{file_name}:{line_number}: DUPLICATE_FLIGHT | {original}"
                    )
                    continue

                seen_flights.add(duplicate_key)
                records.append(to_record(fields))

    return records, errors