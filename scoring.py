"""Score aggregation helpers for risk and confidence computation."""

from __future__ import annotations

from dataclasses import dataclass

from utils import clamp, round_score


@dataclass
class ScoreBundle:
    """Container for component scores and weighted score calculations."""
    physical_score: float
    escalation_score: float
    evidence_score: float
    signal_score: float
    model_score: float

    def risk_score(self) -> float:
        """Compute weighted risk from physical, escalation, and evidence components."""
        return round_score(
            0.45 * clamp(self.physical_score)
            + 0.35 * clamp(self.escalation_score)
            + 0.20 * clamp(self.evidence_score)
        )

    def confidence_score(self) -> float:
        """Compute confidence from evidence, signal, and model reliability."""
        return round_score(
            0.50 * clamp(self.evidence_score)
            + 0.30 * clamp(self.signal_score)
            + 0.20 * clamp(self.model_score)
        )


def confidence_band(score: float) -> str:
    """Map a numeric confidence score into low, medium, or high."""
    score = clamp(score)
    if score >= 0.70:
        return "high"
    if score >= 0.40:
        return "medium"
    return "low"
