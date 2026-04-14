import csv
import tempfile
import unittest
from pathlib import Path

from io_csv import read_csv_rows
from scoring import ScoreBundle, confidence_band
from triage import triage_article


class ScoringTests(unittest.TestCase):
    def test_risk_and_confidence_formulas(self):
        scores = ScoreBundle(
            physical_score=0.8,
            escalation_score=0.4,
            evidence_score=0.6,
            signal_score=0.5,
            model_score=0.75,
        )

        self.assertEqual(scores.risk_score(), 0.62)
        self.assertEqual(scores.confidence_score(), 0.60)
        self.assertEqual(confidence_band(scores.confidence_score()), "medium")


class TriageTests(unittest.TestCase):
    def test_detects_concrete_hormuz_disruption(self):
        result = triage_article(
            "Naval units mined approaches to the Strait of Hormuz, forcing tankers to halt transit after a naval incident."
        )

        self.assertTrue(result.is_candidate)
        self.assertEqual(result.event_labels, ["Hormuz Closure"])
        self.assertIn("strait of hormuz", result.keywords_detected)
        self.assertIn("naval incident", result.keywords_detected)

    def test_filters_energy_etf_commentary_noise(self):
        result = triage_article(
            "The energy ETF rose as analysts cited war risk insurance around the Strait of Hormuz, "
            "but the article focused on shares, portfolio weights, dividend yield, expense ratio, and earnings."
        )

        self.assertFalse(result.is_candidate)
        self.assertEqual(result.event_labels, [])
        self.assertEqual(result.keywords_detected, [])


class CsvInputTests(unittest.TestCase):
    def test_requires_fixed_input_schema_columns(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing_schema.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["content"])
                writer.writeheader()
                writer.writerow({"content": "Only content is not enough."})

            with self.assertRaisesRegex(ValueError, "pubDate, link, content, source_id"):
                read_csv_rows(path)

    def test_accepts_required_columns_and_preserves_extra_columns(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "valid_schema.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["pubDate", "link", "content", "source_id", "notes"],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "pubDate": "2026-03-29",
                        "link": "https://example.com",
                        "content": "No relevant event.",
                        "source_id": "manual",
                        "notes": "extra metadata",
                    }
                )

            rows = read_csv_rows(path)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["notes"], "extra metadata")


if __name__ == "__main__":
    unittest.main()
