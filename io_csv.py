from __future__ import annotations
import csv
from pathlib import Path
from typing import list, Dict, optional
from config import DEFAULT_OUTPUT_COLUMNS

def read_csv_rows(path: Path, max_rows: Optional[int] = None) -> List[Dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
    reader = csv.DictReader(handle)
    rows: List[Dict[str, str]] = []

    for index, row in enumerate(reader):
        if max_rows is not None and index >= max_rows:
            break
        rows.append(row)
    return rows

def write_csv_rows(path: Path, rows: List[Dict[str, str]]) -> None:
    if not rows:
        raise ValueError("No rows to write")
    fieldnames = list(rows[0].keys())
   for column in DEFAULT_OUTPUT_COLUMNS:
    if column not in fieldnames:
        fieldnames.append(column)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)



