# Implementation Plan

## Completed

- Implement CLI entrypoint in `main.py`.
- Implement CSV input/output in `io_csv.py`.
- Implement deterministic triage in `triage.py`.
- Implement Responses API classification in `classifier.py`.
- Implement strict structured-output schema and prompts in `prompt_builder.py`.
- Implement deterministic scoring and confidence bands in `scoring.py`.
- Implement offline heuristic fallback for local testing and API failures.
- Add required project documentation.
- Add an optional triage refinement for investment-commentary false positives.
- Add an optional manual evaluation sample and cost-awareness note.

## Operating Assumptions

- The provided input CSV contains a `content` column.
- The taxonomy is intentionally narrow and defined in code.
- Model output is advisory for labels and component scores; final labels and aggregate scores are normalized by deterministic code.
- Missing `OPENAI_API_KEY` should not prevent a local test run.

## Future Improvements

- Add unit tests around triage rules and score formulas.
- Add retry/backoff behavior for transient OpenAI API failures.
- Add batch-size and resume options for very large CSV files.
- Add a formal `SPEC.md` once the assignment specification is available in the repository.
