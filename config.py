from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Settings:
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))
    input_path: Optional[Path] = None
    output_path: Optional[Path] = None
    max_rows: Optional[int] = None
    triage_min_keyword_hits: int = field(
        default_factory=lambda: int(os.getenv("TRIAGE_MIN_KEYWORD_HITS", "1"))
    )
    llm_max_chars: int = field(default_factory=lambda: int(os.getenv("LLM_MAX_CHARS", "6000")))
    use_llm: bool = field(
        default_factory=lambda: os.getenv("USE_OPENAI", "true").strip().lower() not in {"0", "false", "no"}
    )


DEFAULT_OUTPUT_COLUMNS = [
    "event_labels",
    "risk_score",
    "confidence",
    "rationale",
    "keywords_detected",
]
