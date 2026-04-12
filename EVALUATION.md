# Evaluation Sample

The manual sample in `data/evaluation_sample.csv` contains six short articles:

- Four positive examples covering Hormuz, Gulf infrastructure, coalition entry, and Red Sea escalation.
- Two negative examples covering investment commentary and speculative opinion.

## Offline Heuristic Run

Command:

```bash
python3 main.py --input data/evaluation_sample.csv --output /tmp/ai_news_predict_eval.csv --disable-llm
```

Observed results after the triage refinement:

| Case | Expected | Observed | Result |
| --- | --- | --- | --- |
| Hormuz operational disruption | `Hormuz Closure` | `Hormuz Closure` | Pass |
| Energy ETF commentary | none | none | Pass |
| Abqaiq drone attack | `Critical Gulf Infrastructure Attacks` | `Critical Gulf Infrastructure Attacks` | Pass |
| Saudi/UAE coalition deployment | `Direct Entry of Saudi/UAE/Coalition Forces` | `Direct Entry of Saudi/UAE/Coalition Forces` | Pass |
| Red Sea vessel rerouting | `Red Sea / Bab el-Mandeb Escalation` | `Red Sea / Bab el-Mandeb Escalation` | Pass |
| Speculative opinion | none | none | Pass |

## Strengths

- The triage rules are high precision for concrete operational language.
- Deterministic post-processing keeps scores and labels stable even when model output varies.
- The investment-commentary refinement reduces a common false positive pattern: articles whose main subject is an ETF, stock, or portfolio rather than a new reported event.

## Failure Cases To Watch

- Short breaking-news headlines may lack enough anchor/signal context and be missed.
- Articles with both market analysis and a genuine new operational report can be hard to separate.
- Synonyms outside the current keyword lists will need periodic updates.
