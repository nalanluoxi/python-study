from __future__ import annotations

import argparse
import json
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Union

import pyarrow.parquet as pq

try:
    from openpyxl import Workbook
except ModuleNotFoundError as exc:  # pragma: no cover
    Workbook = None
    OPENPYXL_IMPORT_ERROR = exc
else:
    OPENPYXL_IMPORT_ERROR = None

DEFAULT_PARQUET = Path("/Volumes/WenshuSpace/下载/parsed-stage.parquet")
DEFAULT_OUTPUT = Path("/Users/nalan/IdeaProjects/python-test/py/ReadParquetData/data.xlsx")
EXCEL_MAX_ROWS = 1_048_576
EXCEL_DATA_ROWS_PER_SHEET = EXCEL_MAX_ROWS - 1
EXCEL_NATIVE_TYPES = (str, int, float, bool, date, datetime, time, timedelta, Decimal)


def _normalize_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple, set)):
        return json.dumps(value, ensure_ascii=False, default=str)
    if isinstance(value, EXCEL_NATIVE_TYPES):
        return value
    return str(value)


def _create_worksheet(workbook: Workbook, column_names: list[str], sheet_index: int):
    title = "ParquetData" if sheet_index == 1 else f"ParquetData{sheet_index}"
    worksheet = workbook.create_sheet(title=title)
    worksheet.append(column_names)
    return worksheet


def read_parquet_and_save_as_excel(
        parquet_path: Union[str, Path],
        output_path: Union[str, Path],
        batch_size: int = 5000,
) -> int:
    source = Path(parquet_path)
    target = Path(output_path)

    if not source.exists():
        raise FileNotFoundError(f"Parquet file not found: {source}")
    if not source.is_file():
        raise ValueError(f"Expected a parquet file, got: {source}")
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than 0")
    if Workbook is None:
        raise ModuleNotFoundError(
            "openpyxl is required to export Excel files. Install it with `python -m pip install openpyxl`."
        ) from OPENPYXL_IMPORT_ERROR

    target.parent.mkdir(parents=True, exist_ok=True)

    parquet_file = pq.ParquetFile(str(source))
    column_names = parquet_file.schema_arrow.names
    total_rows = 0

    workbook = Workbook(write_only=True)
    sheet_index = 1
    rows_in_current_sheet = 0
    worksheet = _create_worksheet(workbook, column_names, sheet_index)

    for batch in parquet_file.iter_batches(batch_size=batch_size):
        for row in batch.to_pylist():
            if rows_in_current_sheet >= EXCEL_DATA_ROWS_PER_SHEET:
                sheet_index += 1
                worksheet = _create_worksheet(workbook, column_names, sheet_index)
                rows_in_current_sheet = 0

            worksheet.append([_normalize_value(row.get(column_name)) for column_name in column_names])
            rows_in_current_sheet += 1
            total_rows += 1

    workbook.save(target)
    workbook.close()
    return total_rows


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read a parquet file and save it as an Excel workbook.",
    )
    parser.add_argument(
        "parquet_path",
        nargs="?",
        default=str(DEFAULT_PARQUET),
        help="Path to the source parquet file.",
    )
    parser.add_argument(
        "output_path",
        nargs="?",
        default=str(DEFAULT_OUTPUT),
        help="Path to the output xlsx file.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5000,
        help="Number of rows to read per batch.",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()

    try:
        row_count = read_parquet_and_save_as_excel(
            parquet_path=args.parquet_path,
            output_path=args.output_path,
            batch_size=args.batch_size,
        )
    except Exception as exc:  # pragma: no cover
        print(f"Failed to export parquet file: {exc}")
        return 1

    print(f"Done. Wrote {row_count} rows to {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

