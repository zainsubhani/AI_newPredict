from __future__ import annotations

from dataclasses import dataclass

from utils import clamp, round_score


@dataclass
class ScoreBundle:
    physical_score: float
    escalation_score: float
    evidence_score: float
    signal_score: float
    model_score: float

    def risk_score(self) -> float:
        return round_score(
            0.45 * clamp(self.physical_score)
            + 0.35 * clamp(self.escalation_score)
            + 0.20 * clamp(self.evidence_score)
        )

    def confidence_score(self) -> float:
        return round_score(
            0.50 * clamp(self.evidence_score)
            + 0.30 * clamp(self.signal_score)
            + 0.20 * clamp(self.model_score)
        )


def confidence_band(score: float) -> str:
    score = clamp(score)
    if score >= 0.70:
        return "high"
    if score >= 0.40:
        return "medium"
    return "low"
