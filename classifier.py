"""Article classification logic with OpenAI and heuristic fallback paths."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Union

from config import Settings
from prompt_builder import build_system_prompt, build_user_prompt, classifier_schema
from scoring import ScoreBundle, confidence_band
from triage import EVENT_TAXONOMY
from utils import clamp, dedupe_preserve_order, extract_json_object, lowercase_text, normalize_text, round_score


@dataclass
class ClassificationResult:
    """Normalized classification output consumed by CSV export."""
    event_labels: List[str]
    physical_score: float
    escalation_score: float
    evidence_score: float
    signal_score: float
    model_score: float
    risk_score: float
    confidence_score: float
    confidence: str
    rationale: str
    keywords_detected: List[str]

    def final_columns(self) -> Dict[str, Union[str, float]]:
        return {
            "event_labels": str(self.event_labels),
            "risk_score": self.risk_score,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "keywords_detected": str(self.keywords_detected),
        }


class ArticleClassifier:
    """Classify article risk signals using model inference or heuristics."""
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client = None

    def classify(self, article: Dict[str, str], triage_labels: List[str], triage_keywords: List[str]) -> ClassificationResult:
        """Run primary classification flow and fallback safely on API errors."""
        if self.settings.use_llm and self.settings.openai_api_key:
            try:
                return self._classify_with_openai(article, triage_labels, triage_keywords)
            except Exception as exc:
                fallback = self._heuristic_classify(article, triage_labels, triage_keywords)
                fallback.rationale = f"{fallback.rationale} Fallback used after OpenAI error: {exc.__class__.__name__}."
                return fallback
        return self._heuristic_classify(article, triage_labels, triage_keywords)

    def _client_instance(self):
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(api_key=self.settings.openai_api_key)
        return self._client

    def _classify_with_openai(
        self,
        article: Dict[str, str],
        triage_labels: List[str],
        triage_keywords: List[str],
    ) -> ClassificationResult:
        """Request structured classification output from the OpenAI Responses API."""
        client = self._client_instance()
        response = client.responses.create(
            model=self.settings.openai_model,
            input=[
                {"role": "system", "content": [{"type": "input_text", "text": build_system_prompt()}]},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": build_user_prompt(
                                article=article,
                                triage_labels=triage_labels,
                                keywords_detected=triage_keywords,
                                max_chars=self.settings.llm_max_chars,
                            ),
                        }
                    ],
                },
            ],
            text={"format": {"type": "json_schema", "name": classifier_schema()["name"], "schema": classifier_schema()["schema"], "strict": True}},
        )

        payload = extract_json_object(response.output_text)
        return self._normalize_payload(payload, triage_keywords)

    def _heuristic_classify(
        self,
        article: Dict[str, str],
        triage_labels: List[str],
        triage_keywords: List[str],
    ) -> ClassificationResult:
        """Compute conservative scores from rule-based keyword signals."""
        content = lowercase_text(article.get("content", ""))
        operational_terms = [
            "attack",
            "struck",
            "halt",
            "damaged",
            "hit",
            "seized",
            "reroute",
            "closed",
            "deployment",
            "troops",
            "missile",
            "drone",
        ]
        speculation_terms = [
            "could",
            "may",
            "might",
            "warning",
            "warned",
            "speculation",
            "opinion",
            "commentary",
            "if ",
            "scenario",
        ]

        operational_hits = sum(term in content for term in operational_terms)
        speculation_hits = sum(term in content for term in speculation_terms)

        physical_score = 0.15
        escalation_score = 0.10
        evidence_score = 0.20

        if any(label == "Hormuz Closure" for label in triage_labels):
            physical_score += 0.35
            escalation_score += 0.20
        if any(label == "Critical Gulf Infrastructure Attacks" for label in triage_labels):
            physical_score += 0.25
            escalation_score += 0.10
        if any(label == "Direct Entry of Saudi/UAE/Coalition Forces" for label in triage_labels):
            escalation_score += 0.35
        if any(label == "Red Sea / Bab el-Mandeb Escalation" for label in triage_labels):
            physical_score += 0.15
            escalation_score += 0.20
        if any(label == "Kharg/Khark Attack or Seizure" for label in triage_labels):
            physical_score += 0.30
            escalation_score += 0.15

        physical_score += min(0.20, operational_hits * 0.03)
        evidence_score += min(0.35, operational_hits * 0.04)
        evidence_score -= min(0.20, speculation_hits * 0.04)

        if not triage_labels:
            physical_score = 0.05
            escalation_score = 0.05
            evidence_score = 0.15

        signal_score = clamp(0.30 + min(0.40, len(triage_keywords) * 0.04) + min(0.20, operational_hits * 0.02))
        model_score = clamp(0.75 if len(triage_labels) == 1 else 0.55 if triage_labels else 0.25)

        scores = ScoreBundle(
            physical_score=clamp(physical_score),
            escalation_score=clamp(escalation_score),
            evidence_score=clamp(evidence_score),
            signal_score=signal_score,
            model_score=model_score,
        )
        risk_score = scores.risk_score()
        confidence_score = scores.confidence_score()

        rationale = self._build_heuristic_rationale(triage_labels, triage_keywords, operational_hits, speculation_hits, risk_score)
        return ClassificationResult(
            event_labels=triage_labels,
            physical_score=round_score(scores.physical_score),
            escalation_score=round_score(scores.escalation_score),
            evidence_score=round_score(scores.evidence_score),
            signal_score=round_score(scores.signal_score),
            model_score=round_score(scores.model_score),
            risk_score=risk_score,
            confidence_score=confidence_score,
            confidence=confidence_band(confidence_score),
            rationale=rationale,
            keywords_detected=triage_keywords,
        )

    def _build_heuristic_rationale(
        self,
        triage_labels: List[str],
        triage_keywords: List[str],
        operational_hits: int,
        speculation_hits: int,
        risk_score: float,
    ) -> str:
        if not triage_labels:
            return "No target event taxonomy matched strongly enough; article treated as background noise."

        parts = [
            f"Matched event categories: {', '.join(triage_labels)}.",
            f"Detected keywords: {', '.join(triage_keywords[:8])}.",
        ]
        if operational_hits:
            parts.append(f"Operational language appears {operational_hits} time(s), which supports relevance.")
        if speculation_hits:
            parts.append(f"Speculative language appears {speculation_hits} time(s), so scoring stays conservative.")
        parts.append(f"Final risk score is {risk_score:.2f}.")
        return " ".join(parts)

    def _normalize_payload(self, payload: Dict, triage_keywords: List[str]) -> ClassificationResult:
        labels = [label for label in payload.get("event_labels", []) if label in EVENT_TAXONOMY]
        scores = ScoreBundle(
            physical_score=clamp(float(payload.get("physical_score", 0.0))),
            escalation_score=clamp(float(payload.get("escalation_score", 0.0))),
            evidence_score=clamp(float(payload.get("evidence_score", 0.0))),
            signal_score=clamp(float(payload.get("signal_score", 0.0))),
            model_score=clamp(float(payload.get("model_score", 0.0))),
        )
        risk_score = scores.risk_score()
        confidence_score = scores.confidence_score()
        merged_keywords = dedupe_preserve_order(
            [normalize_text(item) for item in payload.get("keywords_detected", []) if str(item).strip()]
            + triage_keywords
        )
        rationale = normalize_text(str(payload.get("rationale", ""))) or "No rationale returned."
        return ClassificationResult(
            event_labels=labels,
            physical_score=round_score(scores.physical_score),
            escalation_score=round_score(scores.escalation_score),
            evidence_score=round_score(scores.evidence_score),
            signal_score=round_score(scores.signal_score),
            model_score=round_score(scores.model_score),
            risk_score=risk_score,
            confidence_score=confidence_score,
            confidence=confidence_band(confidence_score),
            rationale=rationale,
            keywords_detected=merged_keywords,
        )
