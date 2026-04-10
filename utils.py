"""Shared utility helpers for text normalization, scoring, and JSON parsing."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List


WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Collapse repeated whitespace and trim surrounding spaces."""
    return WHITESPACE_RE.sub(" ", (text or "")).strip()


def lowercase_text(text: str) -> str:
    """Normalize then lowercase text for case-insensitive matching."""
    return normalize_text(text).lower()


def dedupe_preserve_order(items: List[str]) -> List[str]:
    """Remove duplicates while keeping first-seen item order."""
    seen: set[str] = set()
    ordered: List[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    """Bound numeric values into an inclusive range."""
    return max(lower, min(upper, value))


def round_score(value: float) -> float:
    """Clamp and round score values to two decimals."""
    return round(clamp(value), 2)


def to_json_list(items: List[str]) -> str:
    """Serialize a list as a compact JSON array string."""
    return json.dumps(items, ensure_ascii=True)


def extract_json_object(text: str) -> Dict[str, Any]:
    """Parse a JSON object, recovering from wrapped non-JSON text when possible."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in model response.")
    return json.loads(text[start : end + 1])
