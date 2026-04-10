# AI News Risk Predictor

This project processes news articles from a CSV file and predicts **geopolitical macro-risk** relevance using a two-stage pipeline:

1. **Keyword triage** to detect likely event candidates.
2. **Risk classification** (OpenAI model or heuristic fallback) to score severity and confidence.

It outputs an enriched CSV that is ready for downstream analysis.

## Why This Project Is Useful

- Demonstrates practical NLP pipeline design for noisy real-world text.
- Combines rule-based precision (triage) with model-based reasoning (classification).
- Produces transparent outputs with rationale and detected keywords.
- Includes a no-API fallback path for offline/local testing.

## Core Features

- Event taxonomy mapping for high-impact geopolitical scenarios.
- Weighted risk scoring and confidence scoring.
- Structured JSON-schema model output handling.
- Batch processing from input CSV to enriched output CSV.

## Project Structure

- `main.py` - CLI entrypoint and pipeline orchestration.
- `triage.py` - taxonomy, strict matching rules, and candidate selection.
- `classifier.py` - OpenAI classification + heuristic fallback.
- `prompt_builder.py` - system/user prompts and output schema.
- `scoring.py` - risk and confidence score aggregation.
- `io_csv.py` - CSV read/write utilities.
- `config.py` - runtime settings from environment/CLI.
- `utils.py` - shared text and JSON helper functions.

## Input and Output

### Expected Input
Input CSV should include a `content` column (article text). Other metadata columns are preserved.

### Output Columns Added

- `event_labels`
- `risk_score`
- `confidence`
- `rationale`
- `keywords_detected`

## Setup

1. Create and activate a Python environment.
2. Install dependencies:

```bash
python3 -m pip install -r requirement.txt
```

> Note: the dependency file in this repository is `requirement.txt`.

3. (Optional) Add environment variables in `.env`:

```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
USE_OPENAI=true
TRIAGE_MIN_KEYWORD_HITS=1
LLM_MAX_CHARS=6000
```

If `OPENAI_API_KEY` is missing (or `--disable-llm` is used), the app runs with heuristic classification.

## Run

```bash
python3 main.py --input data/newsdata_oil.csv --output outputs/result.csv
```

Optional flags:

- `--max-rows 100`
- `--triage-min-keyword-hits 2`
- `--disable-llm`

## Example Use Case

Use this pipeline to quickly screen large volumes of news and highlight articles likely to impact energy markets, shipping lanes, or regional conflict risk.



This repository showcases:

- Python software engineering fundamentals (modular architecture, typed code, CLI tooling).
- Applied LLM integration using structured outputs and schema validation.
- Hybrid AI approach (rules + model) designed for reliability in production-like workflows.
- Practical data pipeline output suitable for analytics and decision support.
