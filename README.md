# Claude Token Dashboard

A terminal dashboard that tracks your [Claude Code](https://claude.ai/code) token usage in real time — no API calls, no external services. It reads the local session files that Claude Code writes to disk.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- Live token usage by model: Opus, Sonnet, Haiku
- Input / Output / Cache write / Cache read breakdown
- Monthly quota bar (calibrated to your plan)
- Today's usage vs. all-time totals
- Top projects by token consumption
- Refreshes every 5 seconds

## Requirements

- Python 3.10+
- [Claude Code](https://claude.ai/code) installed and used at least once
- `rich` library

```bash
pip install rich
```

## Usage

```bash
python3 claude-tokens.py
```

## Configuration

Edit the top of `claude-tokens.py`:

```python
PLAN_NAME            = "Pro ($20/mo)"   # label only
MONTHLY_LIMIT_TOKENS = 10_000_000       # adjust to match your real quota
BILLING_CYCLE_DAY    = 1                # day of month your billing resets
```

Anthropic does not publish exact token limits per plan. Start with the default and tune `MONTHLY_LIMIT_TOKENS` until the percentage matches what Claude Code shows in its own usage indicator.

## Privacy

This script **only reads local files** under `~/.claude/projects/`. It makes no network requests and sends no data anywhere. Nothing leaves your machine.

> **Never commit your `~/.claude/` directory or any `.jsonl` files** — they contain your conversation history.

## How it works

Claude Code saves every API response (including `usage` metadata) to JSONL files under `~/.claude/projects/`. This dashboard parses those files, aggregates token counts by model and date, and renders the result using [rich](https://github.com/Textualize/rich).

## License

MIT
