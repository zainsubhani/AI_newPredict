"""CSV input/output helpers for reading source rows and writing enriched output."""

from __future__ import annotations
import csv
from pathlib import Path
from typing import Dict, List, Optional
from config import DEFAULT_OUTPUT_COLUMNS

def read_csv_rows(path: Path, max_rows: Optional[int] = None) -> List[Dict[str, str]]:
    """Read CSV rows into dictionaries, optionally limiting row count."""
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows: List[Dict[str, str]] = []

        for index, row in enumerate(reader):
            if max_rows is not None and index >= max_rows:
                break
            rows.append(row)
    return rows

def write_enriched_csv(path: Path, rows: List[Dict[str, str]]) -> None:
    """Write enriched rows and ensure required output columns are present."""
    if not rows:
        raise ValueError("No rows to write")
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    for column in DEFAULT_OUTPUT_COLUMNS:
        if column not in fieldnames:
            fieldnames.append(column)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)



