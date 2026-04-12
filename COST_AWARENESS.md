# Cost Awareness

The default model is `gpt-4.1-mini`.

As of April 12, 2026, OpenAI lists `gpt-4.1-mini` text pricing at:

- Input: `$0.40` per 1M tokens.
- Output: `$1.60` per 1M tokens.

The Responses API is billed at the chosen model's token rates, not as a separate surcharge.

Source: https://openai.com/api/pricing

## Estimate Per 100 Articles

Assumption:

- Average input per classified article: 1,500 tokens.
- Average output per classified article: 200 tokens.
- 100 articles all pass triage and are sent to the model.

Calculation:

```text
input cost = 100 * 1,500 / 1,000,000 * $0.40 = $0.060
output cost = 100 * 200 / 1,000,000 * $1.60 = $0.032
total = about $0.092 per 100 model-classified articles
```

If deterministic triage sends only 40 of 100 articles to the model, the estimate falls to about `$0.037` per 100 input articles.

## Cost Reduction

The simplest cost control is already implemented: no-hit triage rows do not call the API. A further improvement would be to truncate article text more aggressively by sending the headline, lead paragraph, and matched keyword window instead of the first `LLM_MAX_CHARS` characters.
