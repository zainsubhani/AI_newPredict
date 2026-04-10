# This postpones evaluation of type hints and keeps annotations flexible.
from __future__ import annotations

# argparse is used to build the command-line interface for the project.
import argparse
# Path handles filesystem paths more safely than raw strings.
from pathlib import Path
# Type hints make the data flow easier to understand.
from typing import Dict, List

# Import the core modules that power each stage of the pipeline.
from classifier import ArticleClassifier
from config import Settings
from io_csv import read_csv_rows, write_enriched_csv
from triage import triage_article
from utils import to_json_list


# Parse CLI arguments so the script can be run from the terminal.
def parse_args() -> argparse.Namespace:
    # Create the parser and describe what this script does.
    parser = argparse.ArgumentParser(description="Classify macro-risk geopolitical news from a CSV file.")
    # Required path to the source CSV.
    parser.add_argument("--input", required=True, help="Path to input CSV")
    # Required path for the output CSV.
    parser.add_argument("--output", required=True, help="Path to output CSV")
    # Optional row limit for quick testing and debugging.
    parser.add_argument("--max-rows", type=int, default=None, help="Optional cap for local testing")
    parser.add_argument(
        "--triage-min-keyword-hits",
        type=int,
        default=1,
        # This lets us control how strict Stage 1 should be.
        help="Minimum keyword matches required to send an article to classification",
    )
    parser.add_argument(
        "--disable-llm",
        action="store_true",
        # Useful for local tests when no API key is available.
        help="Skip the OpenAI API even if OPENAI_API_KEY is set.",
    )
    # Return the parsed CLI arguments to the caller.
    return parser.parse_args()


# Run the full enrichment pipeline across all rows.
def enrich_rows(settings: Settings) -> List[Dict[str, str]]:
    # Load the input CSV rows.
    rows = read_csv_rows(settings.input_path, max_rows=settings.max_rows)
    # Create the classifier once and reuse it for all articles.
    classifier = ArticleClassifier(settings)
    # Collect the final enriched rows here.
    enriched_rows: List[Dict[str, str]] = []

    # Process each article one by one.
    for row in rows:
        # Stage 1: keyword-based triage.
        triage = triage_article(
            content=row.get("content", ""),
            min_keyword_hits=settings.triage_min_keyword_hits,
        )
        # Stage 2: detailed classification and scoring.
        result = classifier.classify(
            article=row,
            triage_labels=triage.event_labels,
            triage_keywords=triage.keywords_detected,
        )
        # Add the required assignment output columns to the original row.
        row.update(
            {
                "event_labels": to_json_list(result.event_labels),
                "risk_score": f"{result.risk_score:.2f}",
                "confidence": result.confidence,
                "rationale": result.rationale,
                "keywords_detected": to_json_list(result.keywords_detected),
            }
        )
        # Save the enriched row.
        enriched_rows.append(row)
    # Return all processed rows for writing.
    return enriched_rows


# Main entry point when the script is run from the terminal.
def main() -> None:
    # Read command-line options.
    args = parse_args()
    # Convert CLI arguments into a single settings object.
    settings = Settings(
        input_path=Path(args.input),
        output_path=Path(args.output),
        max_rows=args.max_rows,
        triage_min_keyword_hits=args.triage_min_keyword_hits,
        use_llm=not args.disable_llm,
    )
    # Run the enrichment pipeline.
    enriched_rows = enrich_rows(settings)
    # Write the final CSV to disk.
    write_enriched_csv(settings.output_path, enriched_rows)
    # Print a short success message so the user knows the run finished.
    print(f"Wrote {len(enriched_rows)} rows to {settings.output_path}")


# This ensures main() only runs when the file is executed directly.
if __name__ == "__main__":
    main()
