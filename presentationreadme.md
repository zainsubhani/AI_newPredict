# Project Presentation: Geopolitical News Risk Detection

## 1. Project Goal

This project builds a Python command-line pipeline that reads a CSV of news articles and detects geopolitical escalation events involving Iran, the United States, Israel, and related regional actors.

The main goal is not to classify every political article. The goal is to find articles that may describe real events with potential macroeconomic impact, especially events that could affect oil flows, shipping lanes, regional escalation, or critical infrastructure.

The system is designed for high precision, so it prefers to be conservative when evidence is weak.

## 2. Input And Output

The input is a CSV file with these required columns:

- `pubDate`
- `link`
- `content`
- `source_id`

The output is also a CSV file. It keeps the original input columns and adds:

- `event_labels`
- `risk_score`
- `confidence`
- `rationale`
- `keywords_detected`

Example command:

```bash
python3 main.py --input data/evaluation_sample.csv --output outputs/result.csv
```

For local testing without calling the OpenAI API:

```bash
python3 main.py --input data/evaluation_sample.csv --output outputs/result.csv --disable-llm
```

For a real dataset:

```bash
python3 main.py --input data/YOUR_REAL_FILE.csv --output outputs/result_submission.csv
```

## 3. Event Taxonomy

The system classifies articles into five predefined event categories:

- `Hormuz Closure`
- `Kharg/Khark Attack or Seizure`
- `Critical Gulf Infrastructure Attacks`
- `Direct Entry of Saudi/UAE/Coalition Forces`
- `Red Sea / Bab el-Mandeb Escalation`

Multi-label classification is allowed, so one article can match more than one category.

## 4. Pipeline Design

The project uses a two-stage pipeline.

Stage 1 is deterministic triage.

The triage step uses event-specific keyword rules. It looks for important anchors and signals such as `Strait of Hormuz`, `naval incident`, `oil facility`, `Abqaiq`, `Houthis`, `Red Sea`, and `Bab el-Mandeb`.

The triage step is intentionally stricter than simple keyword matching. For example, an article that only discusses an energy ETF and mentions Hormuz as background market context should be treated as noise, not automatically as a geopolitical event.

Stage 2 is structured LLM classification.

Candidate articles are sent to the OpenAI Responses API. The model is asked to return structured JSON that includes event labels, component scores, rationale, and detected keywords.

Rows with no triage signal are handled conservatively without an LLM call. This reduces noise and controls API cost.

## 5. Scoring Method

The final `risk_score` is computed from three component scores:

- `physical_score`: how much the article points to real disruption of shipping, oil, energy, or infrastructure.
- `escalation_score`: how much the article suggests broader regional or multinational escalation.
- `evidence_score`: how strongly the article supports the event as real rather than speculative.

The formula is:

```text
risk_score = 0.45 * physical_score + 0.35 * escalation_score + 0.20 * evidence_score
```

The result is rounded to two decimal places and clipped between `0.00` and `1.00`.

The score is not a sentiment score. It estimates the likelihood that the article describes an event with potential macroeconomic shock impact.

## 6. Confidence Method

The final `confidence` is a category:

- `low`
- `medium`
- `high`

It is computed from:

- `evidence_score`
- `signal_score`
- `model_score`

The formula is:

```text
confidence_score = 0.50 * evidence_score + 0.30 * signal_score + 0.20 * model_score
```

Then it is mapped as:

- `high` if `confidence_score >= 0.70`
- `medium` if `0.40 <= confidence_score < 0.70`
- `low` if `confidence_score < 0.40`

Confidence measures how reliable the classification is. It does not measure event severity.

## 7. Key Technical Decisions

The first key decision was to use deterministic triage before the LLM. This keeps the system simple, reduces API calls, and supports high precision.

The second key decision was to use structured outputs from the OpenAI Responses API. This makes the model output easier to validate and use downstream.

The third key decision was to recompute final risk and confidence scores in deterministic Python code. The model can propose component scores, but the final aggregate scores are controlled by the application.

The fourth key decision was to keep the project modular:

- `main.py` handles the command-line pipeline.
- `io_csv.py` handles CSV reading and writing.
- `triage.py` handles keyword triage.
- `prompt_builder.py` builds the model prompt and JSON schema.
- `classifier.py` handles OpenAI classification and fallback behavior.
- `scoring.py` computes risk and confidence.
- `config.py` stores runtime settings.
- `utils.py` contains helper functions.

## 8. Assumptions

The project assumes that input articles are in English.

It assumes the CSV schema includes `pubDate`, `link`, `content`, and `source_id`.

It assumes the five event categories are fixed and should not be expanded unless the specification changes.

It assumes high precision is more important than high recall, so speculative or ambiguous articles should receive conservative labels and scores.

It assumes that OpenAI API access may not always be available locally, so the pipeline includes `--disable-llm` for offline testing.

## 9. Limitations

The triage system may miss relevant articles if they use wording outside the configured keyword rules.

The offline heuristic fallback is useful for testing, but it is not as nuanced as the LLM classification path.

The current pipeline processes rows sequentially.

There is no retry or backoff logic yet for temporary OpenAI API failures.

The sample dataset is small, so calibration should be improved with a larger labeled evaluation set before production use.

## 10. Evaluation

The repository includes a small manual evaluation sample at:

```text
data/evaluation_sample.csv
```

It includes examples for:

- Hormuz disruption
- Gulf infrastructure attack
- Saudi/UAE coalition force entry
- Red Sea or Bab el-Mandeb escalation
- investment commentary noise
- speculative opinion noise

The sample can be run with:

```bash
python3 main.py --input data/evaluation_sample.csv --output outputs/result.csv --disable-llm
```

The generated output is:

```text
outputs/result.csv
```

## 11. Final Summary

This project turns a written risk-detection specification into a working CSV-to-CSV Python pipeline.

It uses a conservative two-stage design:

```text
CSV input
  -> deterministic keyword triage
  -> OpenAI structured classification
  -> deterministic score cleanup
  -> enriched CSV output
```

The most important design principle is high precision: the system should avoid treating normal political discussion, market commentary, or speculation as a real macro-risk event unless there is clear operational evidence.
