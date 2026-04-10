from __future__ import annotations

import json
from typing import Dict, List

from triage import EVENT_TAXONOMY


def build_system_prompt() -> str:
    taxonomy_lines = []
    for label, keywords in EVENT_TAXONOMY.items():
        taxonomy_lines.append(f"- {label}: {', '.join(keywords)}")
    taxonomy_block = "\n".join(taxonomy_lines)

    return (
        "You are classifying news articles for geopolitical macro-risk.\n"
        "Be conservative and optimize for high precision.\n"
        "Do not treat rhetoric, opinion, speculation, or generic market commentary as a real event unless the article describes a reported operational development.\n"
        "Use only the five allowed event labels, and return an empty list when the article is noise.\n"
        "The risk_score must be based on the provided component scores using the exact weighted formula.\n"
        "Allowed taxonomy:\n"
        f"{taxonomy_block}\n"
    )


def build_user_prompt(article: Dict[str, str], triage_labels: List[str], keywords_detected: List[str], max_chars: int) -> str:
    content = (article.get("content") or "")[:max_chars]
    payload = {
        "pubDate": article.get("pubDate", ""),
        "link": article.get("link", ""),
        "source_id": article.get("source_id", ""),
        "triage_event_hints": triage_labels,
        "triage_keywords": keywords_detected,
        "article_content": content,
    }
    return (
        "Classify this article.\n"
        "Return only valid JSON that matches the schema.\n"
        "Use conservative scores when evidence is weak.\n"
        f"{json.dumps(payload, ensure_ascii=True)}"
    )


def classifier_schema() -> dict:
    return {
        "name": "macro_risk_article_classification",
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "event_labels": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": list(EVENT_TAXONOMY.keys()),
                    },
                },
                "physical_score": {"type": "number", "minimum": 0, "maximum": 1},
                "escalation_score": {"type": "number", "minimum": 0, "maximum": 1},
                "evidence_score": {"type": "number", "minimum": 0, "maximum": 1},
                "signal_score": {"type": "number", "minimum": 0, "maximum": 1},
                "model_score": {"type": "number", "minimum": 0, "maximum": 1},
                "risk_score": {"type": "number", "minimum": 0, "maximum": 1},
                "confidence_score": {"type": "number", "minimum": 0, "maximum": 1},
                "rationale": {"type": "string"},
                "keywords_detected": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": [
                "event_labels",
                "physical_score",
                "escalation_score",
                "evidence_score",
                "signal_score",
                "model_score",
                "risk_score",
                "confidence_score",
                "rationale",
                "keywords_detected",
            ],
        },
        "strict": True,
    }
