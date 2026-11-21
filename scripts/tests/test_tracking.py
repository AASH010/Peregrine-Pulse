"""Tests for the tracking contract, metrics, README sync and SVG generation."""

from __future__ import annotations

import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from tracking.cli import main  # noqa: E402
from tracking.metrics import commit_activity, compute_metrics  # noqa: E402
from tracking.plan_parser import parse_plan, validate_plan  # noqa: E402
from tracking.readme_sync import replace_block  # noqa: E402
from tracking.svg_render import badges_svg, milestones_svg, progress_svg, taskmap_svg  # noqa: E402

MILESTONES = "\n".join(f"| M{i} | Milestone {i} | Objective {i} | — |" for i in range(9))
GATES = "\n".join(f"- [ ] M{i}-G1 Gate {i}" for i in range(9))


def make_plan(task_rows: str, gates: str = GATES) -> str:
    return f"""
| Concept | Name | Prefix |
|---|---|---|
| C01 | Lifecycle | LIF |
| C02 | Risk | RSK |

| ID | Name | Objective | Depends on |
|---|---|---|---|
{MILESTONES}

{gates}

| ID | Task | Pri | MS | Depends | Done when | Status |
|---|---|---|---|---|---|---|
{task_rows}
"""


def row(task_id: str, pri="P0", ms="M0", deps="—", status="todo") -> str:
    return f"| {task_id} | Task {task_id} | {pri} | {ms} | {deps} | done when | {status} |"


def errors_for(rows: str) -> list[str]:
    return validate_plan(parse_plan(make_plan(rows)))


def test_real_plan_satisfies_the_contract():
    plan = parse_plan((ROOT / "PROJECT_PLAN.md").read_text(encoding="utf-8"))
    assert validate_plan(plan) == []
    assert len(plan.tasks) > 100
    assert len(plan.milestones) == 9


def test_requirement_ids_are_not_treated_as_tasks():
    plan = parse_plan("| NFR-01 | Honesty | text |\n| FR-01 | Receive | a | b |")
    assert plan.tasks == []


def test_valid_minimal_plan():
    assert errors_for(row("LIF-01") + "\n" + row("RSK-01", deps="LIF-01")) == []


@pytest.mark.parametrize(
    "rows,fragment",
    [
        (row("LIF-01") + "\n" + row("LIF-01"), "duplicate task id"),
        (row("LIF-01", deps="LIF-09"), "unknown task"),
        (row("LIF-01", status="finished"), "invalid status"),
        (row("LIF-01", pri="P9"), "invalid priority"),
        (row("LIF-01", ms="M9"), "invalid milestone"),
        (row("LIF-01", ms="M1") + "\n" + row("RSK-01", ms="M0", deps="LIF-01"), "later milestone"),
        (row("LIF-01", pri="P2") + "\n" + row("RSK-01", deps="LIF-01"), "optional task"),
        (row("LIF-01", deps="RSK-01") + "\n" + row("RSK-01", deps="LIF-01"), "cycle"),
        ("| LIF-01 | only | three |", "columns"),
    ],
)
def test_violations_are_reported(rows, fragment):
    assert any(fragment in e for e in errors_for(rows)), errors_for(rows)


def test_progress_is_derived_from_statuses_only():
    rows = "\n".join(
        [
            row("LIF-01", status="done"),
            row("LIF-02", status="doing"),
            row("RSK-01"),
            row("RSK-02", pri="P2", status="done"),
        ]
    )
    metrics = compute_metrics(parse_plan(make_plan(rows)))
    assert (metrics["core_done"], metrics["core_total"], metrics["core_pct"]) == (1, 3, 33.3)
    assert (metrics["optional_done"], metrics["optional_total"]) == (1, 1)
    m0 = next(m for m in metrics["milestones"] if m["id"] == "M0")
    assert m0["status"] == "in progress"


def test_milestone_needs_both_tasks_and_gates():
    rows = row("LIF-01", status="done")
    unticked = compute_metrics(parse_plan(make_plan(rows)))
    assert next(m for m in unticked["milestones"] if m["id"] == "M0")["status"] != "complete"
    ticked_gates = GATES.replace("- [ ] M0-G1", "- [x] M0-G1")
    ticked = compute_metrics(parse_plan(make_plan(rows, ticked_gates)))
    assert next(m for m in ticked["milestones"] if m["id"] == "M0")["status"] == "complete"
    assert ticked["milestones_done"] == 1 and ticked["milestones_total"] == 8


def test_blocked_task_blocks_the_milestone():
    metrics = compute_metrics(parse_plan(make_plan(row("LIF-01", status="blocked"))))
    assert next(m for m in metrics["milestones"] if m["id"] == "M0")["status"] == "blocked"


def test_optional_milestone_uses_optional_tasks():
    rows = row("LIF-01", pri="P2", ms="M8", status="done")
    gates = GATES.replace("- [ ] M8-G1", "- [x] M8-G1")
    metrics = compute_metrics(parse_plan(make_plan(rows, gates)))
    m8 = next(m for m in metrics["milestones"] if m["id"] == "M8")
    assert m8["status"] == "complete" and m8["optional"]
    assert metrics["milestones_done"] == 0


def test_replace_block_is_idempotent_and_strict():
    text = "a\n<!-- X:START -->\nold\n<!-- X:END -->\nb\n"
    once = replace_block(text, "X", "new")
    assert once == "a\n<!-- X:START -->\nnew\n<!-- X:END -->\nb\n"
    assert replace_block(once, "X", "new") == once
    with pytest.raises(ValueError):
        replace_block("no markers", "X", "new")


def test_svgs_are_well_formed_and_reflect_the_plan():
    plan = parse_plan((ROOT / "PROJECT_PLAN.md").read_text(encoding="utf-8"))
    metrics = compute_metrics(plan)
    for svg in (
        badges_svg(metrics, None),
        badges_svg(metrics, {"last_7_days": 3, "total": 10}),
        progress_svg(metrics, None),
        taskmap_svg(plan),
        milestones_svg(metrics),
    ):
        ET.fromstring(svg)
    tiles = ET.fromstring(taskmap_svg(plan)).findall(".//{http://www.w3.org/2000/svg}title")
    assert len(tiles) == len(plan.tasks) + 1  # one title per tile plus the document title


def test_commit_activity_is_none_outside_git(tmp_path):
    assert commit_activity(tmp_path) is None


def test_cli_write_is_idempotent(tmp_path):
    shutil.copy(ROOT / "PROJECT_PLAN.md", tmp_path / "PROJECT_PLAN.md")
    readme = (
        "<!-- PROGRESS:START -->\n<!-- PROGRESS:END -->\n<!-- MILESTONES:START -->\n<!-- MILESTONES:END -->\n"
    )
    (tmp_path / "README.md").write_text(readme, encoding="utf-8")
    assert main(["--write", "--root", str(tmp_path)]) == 0
    first = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert "task-map.svg" in first and "milestones.svg" in first
    assert main(["--write", "--root", str(tmp_path)]) == 0
    assert (tmp_path / "README.md").read_text(encoding="utf-8") == first
    assert {p.name for p in (tmp_path / "assets" / "status").iterdir()} == {
        "badges.svg",
        "progress.svg",
        "task-map.svg",
        "milestones.svg",
    }


def test_cli_fails_without_touching_readme_on_invalid_plan(tmp_path):
    (tmp_path / "PROJECT_PLAN.md").write_text(make_plan(row("LIF-01", status="oops")), encoding="utf-8")
    original = "<!-- PROGRESS:START -->\nkeep\n<!-- PROGRESS:END -->\n<!-- MILESTONES:START -->\n<!-- MILESTONES:END -->\n"
    (tmp_path / "README.md").write_text(original, encoding="utf-8")
    assert main(["--write", "--root", str(tmp_path)]) == 1
    assert (tmp_path / "README.md").read_text(encoding="utf-8") == original
