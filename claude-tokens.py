#!/usr/bin/env python3
"""Claude token usage dashboard — reads ~/.claude/projects/**/*.jsonl"""

import sys
import subprocess

# Auto-install rich if missing
try:
    from rich.console import Console
except ImportError:
    print("Installing required dependency: rich...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
    from rich.console import Console

import json
import glob
import os
import time
from datetime import datetime, date
from pathlib import Path
from collections import defaultdict

from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.align import Align
from rich import box

# -- Plan config -----------------------------------------------------------
PLAN_NAME            = "Pro ($20/mo)"
MONTHLY_LIMIT_TOKENS = 10_000_000   # tune to match your real quota
BILLING_CYCLE_DAY    = 1            # day of month your billing resets (1-28)
# --------------------------------------------------------------------------

ANTHROPIC_ORANGE = "color(208)"
DIM_COLOR        = "dim white"

MODEL_COLORS = {
    "opus":   "bold magenta",
    "sonnet": "bold cyan",
    "haiku":  "bold green",
}

CLAUDE_LOGO = """\
  ████████╗
 ██╔══════╝
 ██║  ███╗
 ██║   ██║
 ╚██████╔╝
  ╚═════╝ """


def claude_dir() -> Path:
    return Path.home() / ".claude"


def model_family(model_str: str) -> str:
    m = model_str.lower()
    if "opus" in m:   return "opus"
    if "sonnet" in m: return "sonnet"
    if "haiku" in m:  return "haiku"
    return "other"


def billing_cycle_start() -> date:
    today = date.today()
    day   = BILLING_CYCLE_DAY
    if today.day >= day:
        return today.replace(day=day)
    if today.month == 1:
        return date(today.year - 1, 12, day)
    return date(today.year, today.month - 1, day)


def project_name(fpath: Path) -> str:
    """Extract a readable project name from the encoded folder name."""
    parts = fpath.parts
    try:
        idx = next(i for i, p in enumerate(parts) if p == "projects")
        folder = parts[idx + 1]
    except (StopIteration, IndexError):
        return fpath.stem

    # Claude encodes the absolute path as a kebab-case folder name.
    # Strip the home dir prefix so only the project path remains.
    home_encoded = str(Path.home()).replace("\\", "-").replace("/", "-").lstrip("-")
    name = folder.replace(home_encoded, "").lstrip("-")
    return name or folder


def load_usage():
    projects_dir = claude_dir() / "projects"
    files        = list(projects_dir.rglob("*.jsonl")) if projects_dir.exists() else []
    today_date   = date.today()
    cycle_start  = billing_cycle_start()

    def parse_local_date(ts: str):
        if not ts:
            return None
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            return dt.astimezone().date()
        except Exception:
            return None

    def is_today(ts: str) -> bool:
        return parse_local_date(ts) == today_date

    def is_this_cycle(ts: str) -> bool:
        d = parse_local_date(ts)
        return d is not None and d >= cycle_start

    total      = defaultdict(lambda: defaultdict(int))
    today      = defaultdict(lambda: defaultdict(int))
    cycle      = defaultdict(lambda: defaultdict(int))
    by_project = defaultdict(lambda: defaultdict(int))

    for fpath in files:
        proj = project_name(fpath)
        try:
            with open(fpath, "r", errors="replace") as fh:
                for raw in fh:
                    try:
                        d = json.loads(raw)
                    except json.JSONDecodeError:
                        continue
                    msg   = d.get("message", {})
                    usage = msg.get("usage")
                    if not usage:
                        continue
                    family = model_family(msg.get("model", "unknown"))
                    ts_str = d.get("timestamp", "")
                    inp = usage.get("input_tokens", 0) or 0
                    out = usage.get("output_tokens", 0) or 0
                    cc  = usage.get("cache_creation_input_tokens", 0) or 0
                    cr  = usage.get("cache_read_input_tokens", 0) or 0

                    total[family]["input"]        += inp
                    total[family]["output"]       += out
                    total[family]["cache_create"] += cc
                    total[family]["cache_read"]   += cr

                    by_project[proj]["input"]  += inp
                    by_project[proj]["output"] += out

                    if is_today(ts_str):
                        today[family]["input"]        += inp
                        today[family]["output"]       += out
                        today[family]["cache_create"] += cc
                        today[family]["cache_read"]   += cr

                    if is_this_cycle(ts_str):
                        cycle[family]["input"]        += inp
                        cycle[family]["output"]       += out
                        cycle[family]["cache_create"] += cc
                        cycle[family]["cache_read"]   += cr
        except (OSError, PermissionError):
            continue

    return total, today, cycle, by_project


def fmt(n: int) -> str:
    if n >= 1_000_000: return f"{n/1_000_000:.2f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(n)


def pct_bar(used: int, limit: int, width: int = 20) -> Text:
    pct   = min(used / limit, 1.0) if limit else 0
    fill  = int(pct * width)
    bar   = "█" * fill + "░" * (width - fill)
    color = "green" if pct < 0.6 else "yellow" if pct < 0.85 else "red"
    t = Text()
    t.append("[", style=DIM_COLOR)
    t.append(bar, style=color)
    t.append(f"] {pct*100:.1f}%", style=f"bold {color}")
    return t


def total_tokens(data: dict) -> int:
    return sum(d["input"] + d["output"] for d in data.values())


def make_logo_panel() -> Panel:
    logo = Text(CLAUDE_LOGO, style=ANTHROPIC_ORANGE, justify="center")
    sub  = Text(f"Claude Code\nToken Monitor\n{PLAN_NAME}", style=DIM_COLOR, justify="center")
    return Panel(Align.center(logo + sub), border_style=ANTHROPIC_ORANGE, padding=(0, 1))


def make_quota_panel(today: dict, cycle: dict) -> Panel:
    used_cycle = total_tokens(cycle)
    used_today = total_tokens(today)
    pct        = min(used_cycle / MONTHLY_LIMIT_TOKENS, 1.0) if MONTHLY_LIMIT_TOKENS else 0
    color      = "green" if pct < 0.6 else "yellow" if pct < 0.85 else "red"
    cycle_from = billing_cycle_start().isoformat()

    t = Text()
    t.append("Monthly quota  ", style="bold white")
    t.append(f"{fmt(used_cycle)} / {fmt(MONTHLY_LIMIT_TOKENS)} tokens   ", style=DIM_COLOR)
    t.append_text(pct_bar(used_cycle, MONTHLY_LIMIT_TOKENS, width=30))
    t.append(f"\n  Cycle from {cycle_from}  •  Today: {fmt(used_today)} tokens", style=DIM_COLOR)
    t.append(f"\n  (Adjust MONTHLY_LIMIT_TOKENS if % doesn't match Claude's indicator)", style="dim")

    return Panel(t, title=f"[{ANTHROPIC_ORANGE}]Quota — {PLAN_NAME}[/{ANTHROPIC_ORANGE}]",
                 border_style=color, padding=(0, 1))


def make_usage_table(label: str, data: dict, show_share: bool = False) -> Table:
    t = Table(
        title=f"[bold]{label}[/bold]",
        box=box.ROUNDED,
        border_style="grey50",
        show_footer=True,
        expand=True,
    )
    t.add_column("Model",       style="bold", footer="TOTAL")
    t.add_column("Input",       justify="right", footer="")
    t.add_column("Output",      justify="right", footer="")
    t.add_column("Cache Write", justify="right", footer="")
    t.add_column("Cache Read",  justify="right", footer="")
    t.add_column("Total",       justify="right", footer="")
    if show_share:
        t.add_column("Share", justify="right", footer="")

    families    = ["opus", "sonnet", "haiku"]
    grand_total = sum((data[f]["input"] + data[f]["output"]) for f in families if f in data) or 1
    tot_in = tot_out = tot_cc = tot_cr = tot_tok = 0

    for fam in families:
        d = data.get(fam)
        if not d or (d["input"] + d["output"]) == 0:
            continue
        color = MODEL_COLORS.get(fam, "white")
        tok   = d["input"] + d["output"]
        share = tok / grand_total * 100
        row   = [
            f"[{color}]{fam.capitalize()}[/{color}]",
            f"[cyan]{fmt(d['input'])}[/cyan]",
            f"[yellow]{fmt(d['output'])}[/yellow]",
            f"[dim]{fmt(d['cache_create'])}[/dim]",
            f"[dim green]{fmt(d['cache_read'])}[/dim green]",
            f"[bold]{fmt(tok)}[/bold]",
        ]
        if show_share:
            row.append(f"[dim]{share:.0f}%[/dim]")
        t.add_row(*row)
        tot_in  += d["input"];  tot_out += d["output"]
        tot_cc  += d["cache_create"]; tot_cr += d["cache_read"]
        tot_tok += tok

    t.columns[1].footer = f"[cyan]{fmt(tot_in)}[/cyan]"
    t.columns[2].footer = f"[yellow]{fmt(tot_out)}[/yellow]"
    t.columns[3].footer = fmt(tot_cc)
    t.columns[4].footer = fmt(tot_cr)
    t.columns[5].footer = f"[bold]{fmt(tot_tok)}[/bold]"
    return t


def make_projects_table(by_project: dict) -> Table:
    t = Table(
        title="[bold]Top Projects[/bold]",
        box=box.ROUNDED,
        border_style="grey50",
        expand=True,
    )
    t.add_column("Project", no_wrap=True)
    t.add_column("Input",   justify="right")
    t.add_column("Output",  justify="right")
    t.add_column("Total",   justify="right")
    t.add_column("Share",   justify="right")

    grand  = sum(d["input"] + d["output"] for d in by_project.values()) or 1
    ranked = sorted(by_project.items(),
                    key=lambda kv: kv[1]["input"] + kv[1]["output"],
                    reverse=True)[:8]

    for proj, d in ranked:
        tok   = d["input"] + d["output"]
        share = tok / grand * 100
        t.add_row(
            f"[dim]{proj[:40]}[/dim]",
            f"[cyan]{fmt(d['input'])}[/cyan]",
            f"[yellow]{fmt(d['output'])}[/yellow]",
            f"[bold]{fmt(tok)}[/bold]",
            f"[dim]{share:.1f}%[/dim]",
        )
    return t


def make_frame() -> Panel:
    from rich.console import Group

    total, today, cycle, by_project = load_usage()
    now = datetime.now().strftime("%H:%M:%S")

    rows = [
        Columns([make_logo_panel()], align="center", expand=True),
        Text(""),
        make_quota_panel(today, cycle),
        Text(""),
        make_usage_table(f"Today  ({date.today().isoformat()})", today, show_share=True),
        Text(""),
        make_usage_table("All-Time", total),
        Text(""),
        make_projects_table(by_project),
        Align.right(Text(f"Refresh: {now}  •  Ctrl+C to quit", style=DIM_COLOR)),
    ]

    return Panel(
        Group(*rows),
        title=f"[{ANTHROPIC_ORANGE}]◆ Claude Token Dashboard[/{ANTHROPIC_ORANGE}]",
        border_style=ANTHROPIC_ORANGE,
        padding=(0, 1),
    )


def main():
    if not claude_dir().exists():
        print("Error: ~/.claude not found. Is Claude Code installed?")
        sys.exit(1)

    with Live(console=Console(), refresh_per_second=4, screen=True) as live:
        while True:
            live.update(make_frame())
            time.sleep(5)


if __name__ == "__main__":
    main()
