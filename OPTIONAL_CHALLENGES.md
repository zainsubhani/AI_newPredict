# Optional Challenges

## Triage Improvement

Implemented a deterministic false-positive guard in `triage.py` for investment commentary. When an article only matches `Hormuz Closure`, contains multiple market/fund terms, and lacks strong operational terms, triage clears the match.

This keeps simple rule-based triage while reducing cases where ETF, stock, or portfolio articles inherit event labels from background market context.

## Prompt Design Iteration

The classification prompt now tells the model to:

- Use the article's main news claim rather than incidental context.
- Treat prices, ETFs, equities, forecasts, and commentary as weak evidence unless there is a reported operational event.
- Prefer no label when there is no concrete action such as attack, closure, seizure, deployment, damage, or halt.
- Keep rationales short and evidence-focused.

These changes should improve precision and consistency by making the reject criteria explicit and aligning the model's behavior with the deterministic triage goal.

## Evaluation Sample

`data/evaluation_sample.csv` contains six hand-labeled examples. The offline heuristic run matched all six expected label sets after the triage refinement. Details are in `EVALUATION.md`.

## Cost Awareness

`COST_AWARENESS.md` estimates about `$0.092` per 100 model-classified articles for `gpt-4.1-mini` under a 1,500 input token and 200 output token assumption. Deterministic triage lowers cost by skipping non-candidate rows.
