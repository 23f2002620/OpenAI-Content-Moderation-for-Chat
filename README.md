# 🚨 Real-Time Text Moderation System

AI-Powered content filtering using the OpenAI Moderation API (2024+).  
Designed for chat apps, social platforms, and enterprise communication tools to classify text into harmful categories (hate, sexual content, violence, self-harm, scams, harassment, etc.) and perform automated actions based on configurable thresholds.

---

[Optional badges: CI] [Coverage] [License] [PyPI] <!-- Replace with actual badges -->

## Table of Contents

1. [Features](#features)  
2. [Tech Stack](#tech-stack)  
3. [Project Structure](#project-structure)  
4. [Quickstart](#quickstart)  
5. [Configuration](#configuration)  
6. [Moderation Policy (JSON)](#moderation-policy-json)  
7. [Running the Moderation System](#running-the-moderation-system)  
8. [Input / Output formats](#input--output-formats)  
9. [Actions & Thresholds](#actions--thresholds)  
10. [Performance & Cost](#performance--cost)  
11. [Testing & CI](#testing--ci)  
12. [Security & Privacy](#security--privacy)  
13. [Customization & Extensibility](#customization--extensibility)  
14. [Contributing](#contributing)  
15. [License](#license)  
16. [References](#references)

## Features

- Real-time moderation with low latency (typical <500ms per request)
- Category-wise scoring and configurable thresholds
- Automated actions: ALLOW, WARN, BLOCK (configurable)
- Save moderation results to CSV for audit / analytics
- Batch moderation support (CSV input)
- Optional WebSocket integration for streaming / real-time use

## Tech Stack

- Python 3.9+
- OpenAI Python SDK
- pandas (for CSV handling)
- Optional: websockets or any WebSocket server for real-time streaming

## Project Structure

.
├── moderation_runner.py        # Main runner and example CLI
├── moderation_policy.json      # Default thresholds / policy
├── test_messages.csv           # Example input CSV
├── results.csv                 # Example output produced by the runner
├── README.md
└── requirements.txt

## Quickstart

Prereqs:
- Python 3.9+
- An OpenAI API key with moderation access

1. Create a virtual environment (optional but recommended)
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # macOS/Linux
   .venv\Scripts\activate      # Windows
   ```

2. Install packages
   ```bash
   pip install -r requirements.txt
   # or at minimum:
   pip install openai pandas
   ```

3. Set your API key (one of these methods):

   - Environment variable (recommended)
     ```bash
     export OPENAI_API_KEY="your-api-key-here"   # macOS/Linux
     setx OPENAI_API_KEY "your-api-key-here"     # Windows (new console)
     ```
   - Or create a `.env` file in repo root:
     ```
     OPENAI_API_KEY=your-api-key-here
     ```

4. Run the moderation runner
   ```bash
   python moderation_runner.py
   ```

## Configuration

- moderation_policy.json controls category thresholds and actions.
- You can modify thresholds at runtime without changing code.
- The runner respects the JSON policy to decide ALLOW / WARN / BLOCK.

## Moderation Policy (JSON)

Example moderation_policy.json:
```json
{
  "thresholds": {
    "hate": 0.80,
    "self_harm": 0.70,
    "sexual": 0.80,
    "violence": 0.75,
    "harassment": 0.85,
    "scam": 0.60
  },
  "actions": {
    "default": "ALLOW",
    "on_violation": "BLOCK",
    "on_low_confidence_violation": "WARN"
  },
  "warn_confidence_delta": 0.10
}
```
- thresholds: numeric values [0.0, 1.0] indicating category-specific trigger levels.
- actions: map or defaults for how to behave when thresholds are exceeded.
- warn_confidence_delta: optional; if score is within threshold +/- delta you may treat as WARN.

## Running the Moderation System

The runner should:
- Load messages from `test_messages.csv` (or accept single-message CLI calls / HTTP / WebSocket)
- Query OpenAI Moderation API
- Map returned category scores to configured thresholds
- Produce an action: `ALLOW`, `WARN`, or `BLOCK`
- Append results to `results.csv` (with timing & scores)

Example minimal CLI usage (if supported by moderation_runner.py):
```bash
# Batch mode (reads test_messages.csv)
python moderation_runner.py --input test_messages.csv --output results.csv --policy moderation_policy.json

# Single message mode
python moderation_runner.py --message "You are stupid" --policy moderation_policy.json
```

(Adjust parameters per the actual runner implementation in your repo.)

## Input / Output formats

Input CSV (`test_messages.csv`):
```csv
message
Hello, how are you?
I will kill you
Click this link to win money: scam.com
You are stupid
Let's have sex tonight
Have a great day!
```

Output CSV (`results.csv`) columns (example):
- message_text: original message
- flagged_categories: list/JSON array of categories that crossed thresholds
- confidence_scores: JSON object mapping category -> score
- action_taken: ALLOW | WARN | BLOCK
- response_time_ms: integer latency in milliseconds
- model_response_meta: (optional) raw moderation API output / id / timestamp

Example row (CSV-friendly):
```csv
"I will kill you","[""violence""]","{""violence"":0.92}",BLOCK,160
```

## Actions & Thresholds

- ALLOW: message is within configured thresholds for all categories
- WARN: message has marginal scores or matches low-confidence violation rules (soft moderation)
- BLOCK: message exceeds thresholds for one or more high-severity categories

Customize the mapping in moderation_policy.json to fit product risk tolerance.

## Performance & Cost

- Latency: typical single-request latency depends on model & network; aim for <500ms for single messages with a fast model and persistent HTTP connection.
- Batch throughput: prefer batching where possible to increase throughput and reduce per-message overhead.
- Cost example (illustrative):
  - Avg tokens per message: 20
  - Cost per 1K tokens: ~$0.05 (varies by model & pricing date)
  - 10,000 messages -> ~200,000 tokens -> estimated monthly cost ≈ $10–$15
- Measure your own token usage: store sample logs and compute token counts to estimate real costs.

## Testing & CI

- Unit tests: add test coverage for threshold logic, CSV import/export, and API wrappers.
- Mock the OpenAI Moderation API in tests (do not run live calls in CI).
- Add CI workflow badge and a job to run tests using GitHub Actions.

## Security & Privacy

- Never commit API keys into source control.
- Carefully consider retention: avoid storing personally identifiable information (PII) unless necessary; minimize logging of full messages if privacy is a concern.
- If you store raw messages for auditing, encrypt at rest and restrict access.
- Comply with local data protection laws (GDPR, CCPA, etc.) for user content.

## Customization & Extensibility

- Replace CSV with database ingestion (Postgres, Redis) for production usage.
- Add a WebSocket-based moderation pre-check to block messages before they reach downstream services.
- Build a dashboard for analytics from results.csv (or stream results to a BI system).
- Add multi-language detection and language-specific thresholds.
- Integrate with moderation escalation (human review queue) for WARN items.

## Examples & Snippets

Pseudo-code for mapping categories -> actions:
```python
for message in messages:
    response = call_moderation_api(message)
    scores = extract_category_scores(response)
    violations = [cat for cat, s in scores.items() if s >= policy["thresholds"].get(cat, 1.0)]
    if any_high_severity(violations):
        action = "BLOCK"
    elif marginal_scores(scores, policy):
        action = "WARN"
    else:
        action = "ALLOW"
    write_result(message, violations, scores, action)
```

## Contributing

- Please open issues for feature requests or bugs.
- Submit PRs against `main` (or the primary branch used by the repo). Include tests and update requirements if new deps are added.
- Add a CODE_OF_CONDUCT and CONTRIBUTING.md if this repo will accept outside contributors.

## License

Specify your license here (e.g., MIT). Add a LICENSE file in the repo.

## References

- OpenAI Moderation Guide: https://platform.openai.com/docs/guides/moderation
- OpenAI Moderation API Reference: https://platform.openai.com/docs/api-reference/moderations

---

If you'd like, I can:
- Open a PR with this enhanced README for a repository you name (owner/repo) and a target branch, or
- Update this README further with repo-specific badges, exact CLI flags for your runner, and examples based on your moderation_runner.py implementation — provide the repo and branch and I’ll prepare a PR.
