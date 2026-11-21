"""Compute progress, milestone status and commit activity. Standard library only."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .plan_parser import Plan

HEADLINE_MILESTONES = tuple(f"M{i}" for i in range(8))  # M8 is optional: not in the headline
BOT_COMMIT_PATTERN = "^chore(status):"


def _pct(done: int, total: int) -> float:
    return round(100.0 * done / total, 1) if total else 0.0


def compute_metrics(plan: Plan) -> dict:
    """Progress is derived from task statuses only; commits never count."""
    core = [t for t in plan.tasks if t.core]
    optional = [t for t in plan.tasks if not t.core]
    core_done = sum(t.status == "done" for t in core)
    opt_done = sum(t.status == "done" for t in optional)

    concepts = []
    for concept in plan.concepts:
        tasks = [t for t in plan.tasks if t.prefix == concept.prefix]
        c_core = [t for t in tasks if t.core]
        concepts.append(
            {
                "cid": concept.cid,
                "prefix": concept.prefix,
                "name": concept.name,
                "total": len(tasks),
                "done": sum(t.status == "done" for t in tasks),
                "core_total": len(c_core),
                "core_done": sum(t.status == "done" for t in c_core),
            }
        )

    milestones = []
    for ms in plan.milestones:
        tasks = [t for t in plan.tasks if t.ms == ms.id]
        relevant = [t for t in tasks if t.core] or tasks
        gates = [g for g in plan.gates if g.ms == ms.id]
        done = sum(t.status == "done" for t in relevant)
        gates_done = sum(g.checked for g in gates)
        complete = bool(relevant) and done == len(relevant) and gates_done == len(gates)
        if complete:
            status = "complete"
        elif any(t.status == "blocked" for t in tasks):
            status = "blocked"
        elif any(t.status in ("doing", "done") for t in tasks) or gates_done:
            status = "in progress"
        else:
            status = "not started"
        milestones.append(
            {
                "id": ms.id,
                "name": ms.name,
                "status": status,
                "tasks_done": done,
                "tasks_total": len(relevant),
                "gates_done": gates_done,
                "gates_total": len(gates),
                "optional": ms.id not in HEADLINE_MILESTONES,
            }
        )

    headline = [m for m in milestones if not m["optional"]]
    return {
        "core_done": core_done,
        "core_total": len(core),
        "core_pct": _pct(core_done, len(core)),
        "optional_done": opt_done,
        "optional_total": len(optional),
        "optional_pct": _pct(opt_done, len(optional)),
        "milestones_done": sum(m["status"] == "complete" for m in headline),
        "milestones_total": len(headline),
        "concepts": concepts,
        "milestones": milestones,
    }


def commit_activity(repo_root: Path) -> dict | None:
    """Commit activity (a separate metric). Returns None outside a git checkout."""

    def count(*extra: str) -> int:
        out = subprocess.run(
            ["git", "rev-list", "--count", *extra, "HEAD", "--invert-grep", f"--grep={BOT_COMMIT_PATTERN}"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        return int(out.stdout.strip())

    try:
        return {"last_7_days": count("--since=7.days.ago"), "total": count()}
    except (OSError, subprocess.CalledProcessError, ValueError):
        return None
