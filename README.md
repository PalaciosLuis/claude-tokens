# Claude Token Dashboard

A real-time terminal dashboard for Claude Code token usage. Reads local session files — no API calls, no setup.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- Live daily token usage with % of your daily limit
- Token breakdown by model: Opus, Sonnet, Haiku
- Input / Output / Cache write / Cache read tracking
- All-time usage stats
- Top projects by token consumption
- Respects your local timezone
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
PLAN_NAME          = "Pro ($20/mo)"   # label only
DAILY_LIMIT_TOKENS = 500_000          # your daily usage limit
```

To find your daily limit, check your usage in Claude Code and calculate:
- If Claude shows 29% and you've used 110K tokens today, your limit ≈ 110K / 0.29 = 379K tokens/day

Adjust `DAILY_LIMIT_TOKENS` until the percentage matches Claude's indicator.

## How it works

Claude Code saves every API response (including `usage` metadata) to JSONL files under `~/.claude/projects/`. This dashboard parses those files, aggregates token counts by model and date (respecting your local timezone), and renders the result using [rich](https://github.com/Textualize/rich).

## Privacy

This script **only reads local files** under `~/.claude/projects/`. It makes no network requests and sends no data anywhere.

> **Never commit your `~/.claude/` directory or any `.jsonl` files** — they contain your conversation history.

## Display Breakdown

- **Daily usage** — tokens consumed today vs your daily limit
- **Today breakdown** — tokens per model (Opus, Sonnet, Haiku) with share percentage
- **All-Time** — total tokens across all your usage
- **Top Projects** — which projects consumed the most tokens

## License

MIT

<img width="942" height="777" alt="image" src="https://github.com/user-attachments/assets/fdaee2fc-79f7-41b4-9354-3ff0038d2c74" />


