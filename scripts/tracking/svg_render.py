"""Render the status graphics (badges, progress bars, task map, milestone cards) as SVG.

The graphics use their own navy panel so they stay readable on both light and dark READMEs.
Standard library only.
"""

from __future__ import annotations

import math
import textwrap
from xml.sax.saxutils import escape

from .plan_parser import Plan

BG = "#0F2747"
TRACK = "#1B3A63"
TEXT = "#FFFFFF"
MUTED = "#9FB3CC"
C_DONE = "#2EA043"
C_DOING = "#F1584C"
C_BLOCKED = "#B01A26"
C_TODO = "#3A4F6E"
C_OPTIONAL_STROKE = "#F3A3A0"
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"

TASK_COLORS = {"done": C_DONE, "doing": C_DOING, "blocked": C_BLOCKED, "todo": C_TODO}
MILESTONE_COLORS = {
    "complete": C_DONE,
    "in progress": C_DOING,
    "blocked": C_BLOCKED,
    "not started": C_TODO,
}
SHORT_NAMES = {
    "LIF": "Lifecycle",
    "RSK": "Risk",
    "HCA": "Human capability",
    "REG": "Registry",
    "ORC": "Orchestrator",
    "NET": "Connectivity",
    "SAT": "Satellite",
    "MOB": "Mobile",
    "API": "Platform API",
    "DSH": "Dashboard",
    "CLD": "Cloud",
    "DEV": "Dev assistants",
    "SEC": "Security",
    "EVL": "Evaluation",
    "OPS": "Repo and automation",
    "LOC": "Localization",
    "DEC": "Direct contact",
}


def _open(width: int, height: int, title: str, desc: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="t d">'
        f'<title id="t">{escape(title)}</title><desc id="d">{escape(desc)}</desc>'
    )


def _text(
    x: float,
    y: float,
    content: str,
    size: int = 12,
    fill: str = TEXT,
    weight: str = "400",
    anchor: str = "start",
) -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
        f'fill="{fill}" text-anchor="{anchor}">{escape(content)}</text>'
    )


def _bar(x: float, y: float, width: float, height: float, fraction: float, color: str) -> str:
    radius = height / 2
    parts = [f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" fill="{TRACK}"/>']
    if fraction > 0:
        fill_w = max(height, width * min(fraction, 1.0))
        parts.append(
            f'<rect x="{x}" y="{y}" width="{fill_w:.1f}" height="{height}" rx="{radius}" fill="{color}"/>'
        )
    return "".join(parts)


def badges_svg(metrics: dict, activity: dict | None) -> str:
    """Row of label/value badges (core tasks, progress, milestones, optional, commit activity)."""
    commits = "n/a" if activity is None else str(activity["last_7_days"])
    progress_color = (
        C_DONE if metrics["core_total"] and metrics["core_done"] == metrics["core_total"] else "#E5322D"
    )
    items = [
        ("core tasks", f"{metrics['core_done']}/{metrics['core_total']}", "#2C5282"),
        ("progress", f"{metrics['core_pct']:.1f}%", progress_color),
        ("milestones", f"{metrics['milestones_done']}/{metrics['milestones_total']}", "#2C5282"),
        ("optional", f"{metrics['optional_done']}/{metrics['optional_total']}", "#6B7A90"),
        ("commits (7 days)", commits, "#2C5282"),
    ]
    x = 0
    parts = []
    for label, value, color in items:
        lw = int(len(label) * 6.3) + 16
        vw = int(len(value) * 6.8) + 16
        parts.append(
            f'<g transform="translate({x},0)">'
            f'<path d="M3 0H{lw}V22H3a3 3 0 0 1-3-3V3a3 3 0 0 1 3-3Z" fill="#4B5B73"/>'
            f'<path d="M{lw} 0H{lw + vw - 3}a3 3 0 0 1 3 3V19a3 3 0 0 1-3 3H{lw}Z" fill="{color}"/>'
            + _text(lw / 2, 15, label, 11, TEXT, "600", "middle")
            + _text(lw + vw / 2, 15, value, 11, TEXT, "700", "middle")
            + "</g>"
        )
        x += lw + vw + 6
    width = x - 6
    head = _open(
        width,
        22,
        "Project status badges",
        "Core tasks, progress, milestones, optional tasks and commit activity",
    )
    return head + "".join(parts) + "</svg>"


def progress_svg(metrics: dict, activity: dict | None) -> str:
    """Progress bars: actual progress, optional tasks, milestones; commit activity is separate text."""
    width, height = 940, 190
    left, bar_w = 20, 900
    rows = [
        (
            "Actual progress — core tasks (P0 + P1)",
            metrics["core_done"],
            metrics["core_total"],
            metrics["core_pct"],
            18,
            C_DONE,
        ),
        (
            "Milestones complete (M0–M7)",
            metrics["milestones_done"],
            metrics["milestones_total"],
            None,
            12,
            C_DONE,
        ),
        (
            "Optional tasks (P2) — not in the headline",
            metrics["optional_done"],
            metrics["optional_total"],
            metrics["optional_pct"],
            12,
            C_OPTIONAL_STROKE,
        ),
    ]
    parts = [f'<rect width="{width}" height="{height}" rx="10" fill="{BG}"/>']
    y = 30
    for label, done, total, pct, h, color in rows:
        fraction = done / total if total else 0
        shown = f"{done}/{total}" + (f" · {pct:.1f}%" if pct is not None else "")
        parts.append(_text(left, y, label, 13, TEXT, "600"))
        parts.append(_text(left + bar_w, y, shown, 13, MUTED, "600", "end"))
        parts.append(_bar(left, y + 8, bar_w, h, fraction, color))
        y += 8 + h + 22
    if activity is None:
        line = "Commit activity (separate metric): n/a — computed on GitHub"
    else:
        line = f"Commit activity (separate metric): {activity['last_7_days']} in the last 7 days · {activity['total']} total"
    parts.append(_text(left, height - 14, line + " — commits never complete a task", 12, MUTED))
    head = _open(
        width, height, "Project progress", "Actual progress is derived from task statuses in PROJECT_PLAN.md"
    )
    return head + "".join(parts) + "</svg>"


def taskmap_svg(plan: Plan) -> str:
    """Treemap-style map: one equal-size tile per tracked task, grouped by concept."""
    tile, gap, pad, head_h, block_gap, inner_w = 16, 3, 8, 22, 10, 900
    blocks = []
    for concept in plan.concepts:
        tasks = [t for t in plan.tasks if t.prefix == concept.prefix]
        if not tasks:
            continue
        n = len(tasks)
        cols = max(3, math.ceil(math.sqrt(n * 1.7)))
        rows = math.ceil(n / cols)
        label = f"{concept.prefix} {SHORT_NAMES.get(concept.prefix, concept.name)}"
        grid_w = cols * (tile + gap) - gap
        width = max(grid_w, int(len(label) * 6.2)) + 2 * pad
        height = head_h + rows * (tile + gap) - gap + 2 * pad
        blocks.append({"label": label, "tasks": tasks, "cols": cols, "w": width, "h": height})
    blocks.sort(key=lambda b: (-len(b["tasks"]), b["label"]))

    x = y = row_h = 0
    for b in blocks:
        if x and x + b["w"] > inner_w:
            x, y, row_h = 0, y + row_h + block_gap, 0
        b["x"], b["y"] = x, y
        x += b["w"] + block_gap
        row_h = max(row_h, b["h"])
    map_h = y + row_h

    margin, top, legend_h = 20, 34, 34
    width = inner_w + 2 * margin
    height = top + map_h + legend_h + margin
    core_total = sum(t.core for t in plan.tasks)
    optional_total = len(plan.tasks) - core_total
    parts = [f'<rect width="{width}" height="{height}" rx="10" fill="{BG}"/>']
    parts.append(
        _text(
            margin,
            24,
            f"Task map — one tile per tracked task ({core_total} core, {optional_total} optional outlined)",
            13,
            TEXT,
            "600",
        )
    )
    for b in blocks:
        bx, by = margin + b["x"], top + b["y"]
        parts.append(f'<rect x="{bx}" y="{by}" width="{b["w"]}" height="{b["h"]}" rx="6" fill="#16335A"/>')
        parts.append(_text(bx + pad, by + 15, b["label"], 11, TEXT, "600"))
        for i, task in enumerate(b["tasks"]):
            tx = bx + pad + (i % b["cols"]) * (tile + gap)
            ty = by + head_h + pad // 2 + (i // b["cols"]) * (tile + gap)
            stroke = f' stroke="{C_OPTIONAL_STROKE}" stroke-width="1.5"' if not task.core else ""
            parts.append(
                f'<rect x="{tx}" y="{ty}" width="{tile}" height="{tile}" rx="3" '
                f'fill="{TASK_COLORS.get(task.status, C_TODO)}"{stroke}>'
                f"<title>{escape(task.id)} — {escape(task.status)}</title></rect>"
            )
    ly = top + map_h + 22
    lx = margin
    for label, color, stroke in (
        ("Done", C_DONE, False),
        ("In progress", C_DOING, False),
        ("Blocked", C_BLOCKED, False),
        ("To do", C_TODO, False),
        ("Optional (outlined)", C_TODO, True),
    ):
        extra = f' stroke="{C_OPTIONAL_STROKE}" stroke-width="1.5"' if stroke else ""
        parts.append(f'<rect x="{lx}" y="{ly - 11}" width="12" height="12" rx="3" fill="{color}"{extra}/>')
        parts.append(_text(lx + 18, ly, label, 12, MUTED))
        lx += 18 + int(len(label) * 6.4) + 22
    head = _open(
        width, height, "Task map", "Each tile is one tracked task, coloured by status and grouped by concept"
    )
    return head + "".join(parts) + "</svg>"


def milestones_svg(metrics: dict) -> str:
    """Horizontal milestone cards with status, task progress and exit-gate progress."""
    card_w, card_h, gap, margin, top = 100, 172, 10, 20, 42
    count = len(metrics["milestones"])
    width = margin * 2 + count * card_w + (count - 1) * gap
    height = top + card_h + margin
    parts = [f'<rect width="{width}" height="{height}" rx="10" fill="{BG}"/>']
    parts.append(
        _text(
            margin,
            26,
            "Milestones — complete only when all core tasks are done and every exit gate is ticked",
            13,
            TEXT,
            "600",
        )
    )
    parts.append(
        f'<line x1="{margin}" y1="{top + 3}" x2="{width - margin}" y2="{top + 3}" stroke="{C_TODO}" stroke-width="2"/>'
    )
    for i, m in enumerate(metrics["milestones"]):
        x = margin + i * (card_w + gap)
        color = MILESTONE_COLORS[m["status"]]
        dash = ' stroke="#3A4F6E" stroke-dasharray="4 3" stroke-width="1.5"' if m["optional"] else ""
        parts.append(
            f'<rect x="{x}" y="{top}" width="{card_w}" height="{card_h}" rx="8" fill="#16335A"{dash}/>'
        )
        parts.append(f'<rect x="{x}" y="{top}" width="{card_w}" height="6" rx="3" fill="{color}"/>')
        parts.append(_text(x + 10, top + 30, m["id"], 16, TEXT, "700"))
        chip = m["status"].upper()
        parts.append(
            _text(x + 10, top + 46, chip, 8, color if m["status"] != "not started" else MUTED, "700")
        )
        for j, line in enumerate(textwrap.wrap(m["name"], width=15, break_long_words=False)[:4]):
            parts.append(_text(x + 10, top + 66 + j * 13, line, 10, TEXT))
        fraction = m["tasks_done"] / m["tasks_total"] if m["tasks_total"] else 0
        parts.append(_bar(x + 10, top + 126, card_w - 20, 6, fraction, color))
        parts.append(_text(x + 10, top + 148, f"tasks {m['tasks_done']}/{m['tasks_total']}", 10, MUTED))
        parts.append(_text(x + 10, top + 162, f"gates {m['gates_done']}/{m['gates_total']}", 10, MUTED))
    head = _open(width, height, "Milestones", "Milestone status derived from task statuses and exit gates")
    return head + "".join(parts) + "</svg>"
