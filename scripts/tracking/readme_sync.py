"""Render the generated README blocks and replace them between marker comments."""

from __future__ import annotations


def replace_block(text: str, name: str, content: str) -> str:
    """Replace the content between <!-- NAME:START --> and <!-- NAME:END -->."""
    start, end = f"<!-- {name}:START -->", f"<!-- {name}:END -->"
    if start not in text or end not in text:
        raise ValueError(f"README markers for {name} not found")
    head, rest = text.split(start, 1)
    _, tail = rest.split(end, 1)
    return f"{head}{start}\n{content.strip()}\n{end}{tail}"


def _activity_line(activity: dict | None) -> str:
    if activity is None:
        return "**Commit activity** (separate metric): n/a — computed on GitHub."
    return (
        f"**Commit activity** (separate metric): {activity['last_7_days']} commits in the last 7 days, "
        f"{activity['total']} in total. A commit never completes a task."
    )


def progress_block(metrics: dict, activity: dict | None) -> str:
    rows = "\n".join(
        f"| {c['prefix']} · {c['name']} | {c['done']} | {c['total']} | "
        f"{(100 * c['core_done'] / c['core_total']) if c['core_total'] else 0:.0f}% |"
        for c in metrics["concepts"]
    )
    return f"""<p align="center"><img src="assets/status/badges.svg" alt="Status badges"></p>

<p align="center"><img src="assets/status/progress.svg" alt="Project progress bars" width="900"></p>

<p align="center"><img src="assets/status/task-map.svg" alt="Task map: one tile per tracked task" width="900"></p>

**Actual progress:** {metrics["core_done"]} of {metrics["core_total"]} core tasks done ({metrics["core_pct"]:.1f}%). \
Optional tasks: {metrics["optional_done"]} of {metrics["optional_total"]}.

{_activity_line(activity)}

<details>
<summary>Progress by concept</summary>

| Concept | Done | Total | Core done |
|---|---:|---:|---:|
{rows}

</details>"""


def milestones_block(metrics: dict) -> str:
    rows = "\n".join(
        f"| {m['id']} | {m['name']} | {m['status']}{' (optional)' if m['optional'] else ''} | "
        f"{m['tasks_done']}/{m['tasks_total']} | {m['gates_done']}/{m['gates_total']} |"
        for m in metrics["milestones"]
    )
    return f"""<p align="center"><img src="assets/status/milestones.svg" alt="Milestone cards" width="900"></p>

A milestone is complete only when all of its core tasks are done **and** every exit gate is ticked.

| Milestone | Name | Status | Tasks | Gates |
|---|---|---|---:|---:|
{rows}"""
