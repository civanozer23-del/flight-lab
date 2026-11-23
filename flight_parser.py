"""Flight Schedule Parser and Query Tool - command-line entry point."""

import argparse
import csv
import json
import logging
import os
import sys
from datetime import datetime

from csv_loader import parse_files
from query import run_queries
from validator import load_airports


STUDENT_ID = "251ADB130"
FIRST_NAME = "Civan"
LAST_NAME = "Ozer"


def _load_json(path: str):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def _write_json(path: str, data) -> None:
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def main(argv: list[str] | None = None) -> int:
    """Run the whole program and return exit code 0, 1 or 2."""

    parser = argparse.ArgumentParser(
        description="Validate flight schedules and run flight queries."
    )

    sources = parser.add_mutually_exclusive_group(required=True)
    sources.add_argument("-i", metavar="FILE", help="parse one CSV file")
    sources.add_argument("-d", metavar="FOLDER", help="parse CSV files in a folder")
    sources.add_argument("-j", metavar="FILE", help="load an existing JSON database")

    parser.add_argument("-a", metavar="FILE", help="airport list file")
    parser.add_argument("-o", metavar="FILE", default=None, help="database output path")
    parser.add_argument("-q", metavar="FILE", help="query JSON file")
    parser.add_argument("-r", metavar="FOLDER", default=".", help="response folder")

    try:
        args = parser.parse_args(argv)

        if (args.i or args.d) and not args.a:
            parser.error("-a is required with -i or -d")

        if args.j and args.o is not None:
            parser.error("-o cannot be used with -j")

    except SystemExit as exc:
        return int(exc.code)

    handler = None
    logger = logging.getLogger("flight_parser")
    logger.setLevel(logging.INFO)

    try:
        # ------------------------------------------------------------
        # Parse CSV input (-i or -d)
        # ------------------------------------------------------------
        if args.i or args.d:
            output_path = args.o if args.o is not None else "db.json"

            output_folder = os.path.dirname(os.path.abspath(output_path))

            if not os.path.isdir(output_folder):
                raise OSError(f"output folder does not exist: {output_folder}")

            airports = load_airports(args.a)

            if args.i:
                if not os.path.isfile(args.i):
                    raise OSError(f"file does not exist: {args.i}")

                paths = [args.i]

            else:
                if not os.path.isdir(args.d):
                    raise OSError(f"folder does not exist: {args.d}")

                names = sorted(
                    name
                    for name in os.listdir(args.d)
                    if name.endswith(".csv")
                    and os.path.isfile(os.path.join(args.d, name))
                )

                if not names:
                    raise OSError("folder contains no .csv files")

                paths = [os.path.join(args.d, name) for name in names]

            error_log_path = os.path.join(output_folder, "errors.log")

            handler = logging.FileHandler(
                error_log_path,
                mode="w",
                encoding="utf-8",
            )

            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )

            logger.addHandler(handler)

            records, errors = parse_files(paths, airports)

            _write_json(output_path, records)

            for message in errors:
                logger.warning(message)

            database = records

        # ------------------------------------------------------------
        # Load existing JSON database (-j)
        # ------------------------------------------------------------
        else:
            if not os.path.isfile(args.j):
                raise OSError(f"file does not exist: {args.j}")

            database = _load_json(args.j)

            if not isinstance(database, list) or not all(
                isinstance(record, dict) for record in database
            ):
                raise ValueError("database must be a JSON array of objects")

        # ------------------------------------------------------------
        # Optional queries
        # ------------------------------------------------------------
        if args.q:
            if not os.path.isfile(args.q):
                raise OSError(f"query file does not exist: {args.q}")

            queries = _load_json(args.q)

            if isinstance(queries, dict):
                pass
            elif isinstance(queries, list) and all(
                isinstance(query, dict) for query in queries
            ):
                pass
            else:
                raise ValueError(
                    "query file must contain an object or an array of objects"
                )

            if not os.path.isdir(args.r):
                raise OSError(f"response folder does not exist: {args.r}")

            response = run_queries(database, queries)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            response_name = (
                f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{timestamp}.json"
            )

            response_path = os.path.join(args.r, response_name)
            _write_json(response_path, response)

        return 0

    except (OSError, ValueError, json.JSONDecodeError, UnicodeError, csv.Error) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    finally:
        if handler is not None:
            logger.removeHandler(handler)
            handler.close()


if __name__ == "__main__":
    sys.exit(main())