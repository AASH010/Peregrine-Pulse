"""Command line entry for the tracking tools."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .metrics import commit_activity, compute_metrics
from .plan_parser import parse_plan, validate_plan
from .readme_sync import milestones_block, progress_block, replace_block
from .svg_render import badges_svg, milestones_svg, progress_svg, taskmap_svg

DEFAULT_ROOT = Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate PROJECT_PLAN.md and refresh generated status views."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--validate", action="store_true", help="validate the tracking contract only")
    mode.add_argument(
        "--dry-run", action="store_true", help="print the computed metrics as JSON; write nothing"
    )
    mode.add_argument(
        "--write", action="store_true", help="regenerate assets/status/*.svg and the README blocks"
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="repository root")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root: Path = args.root
    plan_path, readme_path, out_dir = root / "PROJECT_PLAN.md", root / "README.md", root / "assets" / "status"

    plan = parse_plan(plan_path.read_text(encoding="utf-8"))
    errors = validate_plan(plan)
    if errors:
        print("PROJECT_PLAN.md violates the tracking contract:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    if args.validate:
        print(
            f"OK: {len(plan.tasks)} tasks, {len(plan.concepts)} concepts, {len(plan.milestones)} milestones, {len(plan.gates)} gates"
        )
        return 0

    metrics = compute_metrics(plan)
    activity = commit_activity(root)
    if args.dry_run:
        print(json.dumps({"metrics": metrics, "commit_activity": activity}, indent=2))
        return 0

    readme = readme_path.read_text(encoding="utf-8")
    updated = replace_block(readme, "PROGRESS", progress_block(metrics, activity))
    updated = replace_block(updated, "MILESTONES", milestones_block(metrics))
    out_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "badges.svg": badges_svg(metrics, activity),
        "progress.svg": progress_svg(metrics, activity),
        "task-map.svg": taskmap_svg(plan),
        "milestones.svg": milestones_svg(metrics),
    }
    for name, content in files.items():
        (out_dir / name).write_text(content, encoding="utf-8")
    readme_path.write_text(updated, encoding="utf-8")
    print(f"Updated README.md and {len(files)} graphics in assets/status/")
    return 0
