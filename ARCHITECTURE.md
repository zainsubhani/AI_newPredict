# Architecture

This project is a command-line CSV enrichment pipeline for geopolitical macro-risk news classification.

## Pipeline

1. CSV input
   - `main.py` parses CLI arguments.
   - `io_csv.py` reads the input CSV and requires a `content` column.
   - Metadata columns such as `pubDate`, `link`, and `source_id` are preserved when present.

2. Deterministic triage
   - `triage.py` applies event-specific anchor/signal/context rules.
   - It returns candidate event labels and detected keywords.
   - Triage is intentionally high precision and does not call external services.

3. LLM classification
   - `classifier.py` calls the OpenAI Responses API when `OPENAI_API_KEY` is present and LLM use is enabled.
   - Rows with no triage label and no detected keyword are handled deterministically and do not call the API.
   - `prompt_builder.py` builds the system prompt, article payload, and strict JSON schema for structured outputs.
   - The model returns component scores, event labels, rationale, and keywords.

4. Deterministic post-processing
   - `classifier.py` filters event labels to the allowed taxonomy.
   - `scoring.py` recomputes final `risk_score` and `confidence` from component scores.
   - Model-supplied numeric values are clamped to `[0, 1]`, rounded, and normalized before export.
   - If the API call fails or LLM use is disabled, a conservative heuristic fallback is used.

5. CSV output
   - `io_csv.py` writes the original columns plus:
     - `event_labels`
     - `risk_score`
     - `confidence`
     - `rationale`
     - `keywords_detected`

## Runtime Dependencies

The only required external package is the OpenAI Python SDK. The pipeline can run offline with `--disable-llm`, but production LLM classification requires `OPENAI_API_KEY`.
