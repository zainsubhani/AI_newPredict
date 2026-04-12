# Data Model

## Input CSV

Required column:

- `content`: article text to classify.

Optional columns used when present:

- `pubDate`: publication timestamp.
- `link`: article URL.
- `source_id`: source identifier.

All input columns are preserved in the output.

## Event Taxonomy

The allowed event labels are defined in `triage.py`:

- `Hormuz Closure`
- `Kharg/Khark Attack or Seizure`
- `Critical Gulf Infrastructure Attacks`
- `Direct Entry of Saudi/UAE/Coalition Forces`
- `Red Sea / Bab el-Mandeb Escalation`

No other model-returned label is accepted in post-processing.

## Output Columns

- `event_labels`: JSON array string of accepted taxonomy labels.
- `risk_score`: decimal score from `0.00` to `1.00`.
- `confidence`: `low`, `medium`, or `high`.
- `rationale`: concise explanation for the classification.
- `keywords_detected`: JSON array string of matched or model-detected keywords.

## Internal Scores

Structured model output includes:

- `physical_score`
- `escalation_score`
- `evidence_score`
- `signal_score`
- `model_score`
- `risk_score`
- `confidence_score`
- `rationale`
- `keywords_detected`

The exported `risk_score` and `confidence` are not trusted directly from the model. They are recomputed deterministically:

```text
risk_score = 0.45 * physical_score + 0.35 * escalation_score + 0.20 * evidence_score
confidence_score = 0.50 * evidence_score + 0.30 * signal_score + 0.20 * model_score
```

Confidence bands:

- `high`: score >= `0.70`
- `medium`: score >= `0.40`
- `low`: score < `0.40`
