from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Dict, List

from utils import dedupe_preserve_order, lowercase_text


EVENT_TAXONOMY: Dict[str, List[str]] = {
    "Hormuz Closure": [
        "hormuz",
        "strait of hormuz",
        "mine",
        "naval mine",
        "mining",
        "tanker attack",
        "vessel attack",
        "ship attack",
        "shipping halt",
        "transit halt",
        "blockade",
        "war risk insurance",
        "insurance spike",
        "naval incident",
        "irgc navy",
    ],
    "Kharg/Khark Attack or Seizure": [
        "kharg",
        "khark",
        "oil terminal",
        "export terminal",
        "landing",
        "amphibious landing",
        "seize",
        "takeover",
        "capture",
        "export halt",
        "loading stop",
        "offshore facilities",
        "loading jetty",
    ],
    "Critical Gulf Infrastructure Attacks": [
        "refinery",
        "oil facility",
        "processing plant",
        "gas plant",
        "lng terminal",
        "desalination",
        "water plant",
        "pipeline",
        "pumping station",
        "saudi",
        "uae",
        "fujairah",
        "abqaiq",
        "ras tanura",
        "drone strike",
        "missile strike",
        "sabotage",
    ],
    "Direct Entry of Saudi/UAE/Coalition Forces": [
        "coalition",
        "multinational force",
        "ground forces",
        "troop deployment",
        "amphibious operation",
        "saudi intervention",
        "uae intervention",
        "joint operation",
        "allied response",
        "escalation",
        "regional war",
    ],
    "Red Sea / Bab el-Mandeb Escalation": [
        "houthis",
        "houthi attacks",
        "red sea",
        "bab el-mandeb",
        "merchant vessels",
        "cargo ships",
        "shipping reroute",
        "diversion",
        "naval escort",
        "convoy",
    ],
}

# EVENT_RULES is stricter than the raw taxonomy.
# We separate anchors, signals, and optional context so triage stays high precision.
EVENT_RULES = {
    "Hormuz Closure": {
        "anchors": ["hormuz", "strait of hormuz"],
        "signals": [
            "mine",
            "naval mine",
            "mining",
            "tanker attack",
            "vessel attack",
            "ship attack",
            "shipping halt",
            "transit halt",
            "blockade",
            "war risk insurance",
            "insurance spike",
            "naval incident",
            "irgc navy",
            "traffic remains disrupted",
            "slowed to a trickle",
            "reopen hormuz",
            "choked off",
            "barring most vessels",
        ],
    },
    "Kharg/Khark Attack or Seizure": {
        "anchors": ["kharg", "khark", "oil terminal", "export terminal", "loading jetty", "offshore facilities"],
        "signals": [
            "landing",
            "amphibious landing",
            "seize",
            "seized",
            "takeover",
            "capture",
            "captured",
            "export halt",
            "loading stop",
            "attack",
            "strike",
            "damage",
        ],
    },
    "Critical Gulf Infrastructure Attacks": {
        "anchors": [
            "refinery",
            "oil facility",
            "processing plant",
            "gas plant",
            "lng terminal",
            "desalination",
            "water plant",
            "pipeline",
            "pumping station",
            "fujairah",
            "abqaiq",
            "ras tanura",
            "industrial site",
            "port",
        ],
        "signals": ["drone strike", "missile strike", "sabotage", "attack", "struck", "hit", "damaged", "fires"],
        "context": ["saudi", "uae", "gulf", "oman", "bahrain", "abu dhabi"],
    },
    "Direct Entry of Saudi/UAE/Coalition Forces": {
        "anchors": [
            "coalition",
            "multinational force",
            "ground forces",
            "troop deployment",
            "amphibious operation",
            "joint operation",
            "allied response",
        ],
        "signals": ["saudi", "uae", "american soldiers", "marines", "troops arrived", "ground operations"],
    },
    "Red Sea / Bab el-Mandeb Escalation": {
        "anchors": ["houthis", "houthi attacks", "red sea", "bab el-mandeb"],
        "signals": [
            "merchant vessels",
            "cargo ships",
            "shipping reroute",
            "diversion",
            "naval escort",
            "convoy",
            "target vessels",
            "western shippers",
            "reroute",
            "missile range",
            "shut the red sea",
        ],
    },
}


@dataclass
class TriageResult:
    is_candidate: bool
    event_labels: List[str]
    keywords_detected: List[str]
    keyword_hit_count: int


def _contains_phrase(text: str, phrase: str) -> bool:
    pattern = re.compile(rf"(?<!\w){re.escape(phrase.lower())}(?!\w)")
    return bool(pattern.search(text))


def _find_hits(text: str, phrases: List[str]) -> List[str]:
    return [phrase for phrase in phrases if _contains_phrase(text, phrase)]


def triage_article(content: str, min_keyword_hits: int = 1) -> TriageResult:
    haystack = lowercase_text(content)
    matched_labels: List[str] = []
    matched_keywords: List[str] = []

    for event_label, keywords in EVENT_TAXONOMY.items():
        rules = EVENT_RULES[event_label]
        anchor_hits = _find_hits(haystack, rules.get("anchors", []))
        signal_hits = _find_hits(haystack, rules.get("signals", []))
        context_hits = _find_hits(haystack, rules.get("context", []))
        matched = False
        if event_label == "Hormuz Closure":
            matched = bool(anchor_hits) and (bool(signal_hits) or len(anchor_hits) >= 2)
        elif event_label == "Kharg/Khark Attack or Seizure":
            matched = bool(anchor_hits) and bool(signal_hits)
        elif event_label == "Critical Gulf Infrastructure Attacks":
            matched = bool(anchor_hits) and bool(signal_hits) and (bool(context_hits) or any(x in anchor_hits for x in ["fujairah", "abqaiq", "ras tanura"]))
        elif event_label == "Direct Entry of Saudi/UAE/Coalition Forces":
            matched = bool(anchor_hits) and bool(signal_hits)
        elif event_label == "Red Sea / Bab el-Mandeb Escalation":
            matched = bool(anchor_hits) and (bool(signal_hits) or len(anchor_hits) >= 2)

        if matched:
            event_hits = _find_hits(haystack, keywords)
            matched_labels.append(event_label)
            matched_keywords.extend(event_hits)

    matched_keywords = dedupe_preserve_order(matched_keywords)
    is_candidate = len(matched_keywords) >= min_keyword_hits
    return TriageResult(
        is_candidate=is_candidate,
        event_labels=matched_labels if is_candidate else [],
        keywords_detected=matched_keywords,
        keyword_hit_count=len(matched_keywords),
    )
