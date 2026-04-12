# AI News Risk Predictor

This project processes news articles from a CSV file and writes an enriched CSV with geopolitical macro-risk labels, scores, confidence, rationale, and detected keywords.

The pipeline follows the requested structure:

1. Deterministic triage.
2. LLM-based classification through the OpenAI Responses API with structured outputs.
3. Deterministic post-processing for taxonomy filtering, scoring, confidence bands, and CSV export.

## Project Structure

- `main.py`: CLI entrypoint and pipeline orchestration.
- `triage.py`: taxonomy, matching rules, and candidate detection.
- `classifier.py`: Responses API classification and heuristic fallback.
- `prompt_builder.py`: prompts and strict structured-output schema.
- `scoring.py`: deterministic risk and confidence formulas.
- `io_csv.py`: CSV read/write helpers.
- `config.py`: runtime settings from CLI and environment variables.
- `utils.py`: text, JSON, and score helpers.
- `ARCHITECTURE.md`: pipeline design.
- `DATA_MODEL.md`: input, output, taxonomy, and score model.
- `IMPLEMENTATION_PLAN.md`: implementation status and future work.
- `EVALUATION.md`: manual sample results and failure cases.
- `COST_AWARENESS.md`: approximate LLM cost and cost-control suggestion.
- `OPTIONAL_CHALLENGES.md`: triage, prompt, evaluation, and cost notes.

## Input

The input CSV must include:

- `content`: article text.

Optional metadata columns such as `pubDate`, `link`, and `source_id` are passed through to the output.

## Output

The output CSV preserves all input columns and adds:

- `event_labels`
- `risk_score`
- `confidence`
- `rationale`
- `keywords_detected`

## Setup

Create a Python environment and install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

The legacy `requirement.txt` file is also kept with the same dependency for compatibility.

For LLM classification, set:

```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
USE_OPENAI=true
TRIAGE_MIN_KEYWORD_HITS=1
LLM_MAX_CHARS=6000
```

If `OPENAI_API_KEY` is missing or `--disable-llm` is used, the pipeline runs with deterministic triage plus heuristic scoring.

## Run

```bash
python3 main.py --input data/newsdata_oil.csv --output outputs/result.csv
```

Useful options:

```bash
python3 main.py --input data/newsdata_oil.csv --output outputs/sample.csv --max-rows 25
python3 main.py --input data/newsdata_oil.csv --output outputs/offline.csv --disable-llm
python3 main.py --input data/newsdata_oil.csv --output outputs/strict.csv --triage-min-keyword-hits 2
```
