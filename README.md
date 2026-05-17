# Claude Token Dashboard

A real-time terminal dashboard for Claude Code token usage. Reads local session files — no API calls, no setup.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- Live token usage by model: Opus, Sonnet, Haiku
- Input / Output / Cache write / Cache read breakdown
- Monthly quota bar calibrated to your billing cycle
- Today's usage vs. all-time totals
- Top projects by token consumption
- Refreshes every 5 seconds
- Works on Linux, macOS, and Windows

## Quick Start

### Linux / macOS

```bash
git clone https://github.com/YOUR_USER/claude-tokens
cd claude-tokens
./run.sh
```

> `run.sh` auto-detects your Python (including pyenv) and installs `rich` if missing.

### Windows

```
1. Clone or download this repo
2. Double-click run.bat
```

> `run.bat` tries `py`, `python`, `python3`, and pyenv-win automatically.  
> If Python isn't installed, download it from https://python.org — check **"Add Python to PATH"**.

### Manual

```bash
pip install rich
python3 claude-tokens.py
```

## Configuration

Edit the top of `claude-tokens.py`:

```python
PLAN_NAME            = "Pro ($20/mo)"   # label only
MONTHLY_LIMIT_TOKENS = 10_000_000       # tune to match your real quota
BILLING_CYCLE_DAY    = 1                # day of month your billing resets (1-28)
```

Anthropic does not publish exact token limits per plan. Start with the default and adjust `MONTHLY_LIMIT_TOKENS` until the percentage matches what Claude Code shows in its own usage indicator.

## How it works

Claude Code saves every API response (including `usage` metadata) to JSONL files under `~/.claude/projects/`. This dashboard parses those files, aggregates token counts by model and date, and renders the result using [rich](https://github.com/Textualize/rich).

## Privacy

This script **only reads local files** under `~/.claude/projects/`. It makes no network requests and sends no data anywhere.

> **Never commit your `~/.claude/` directory or any `.jsonl` files** — they contain your conversation history.

## License

MIT

Example:
<img width="937" height="854" alt="image" src="https://github.com/user-attachments/assets/77799b85-271d-45af-9745-1244306b327d" />

