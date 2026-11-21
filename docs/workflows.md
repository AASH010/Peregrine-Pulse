# Automation

Two workflows exist. Nothing here protects the repository; branch rules and access control are a separate, deferred phase.

| Workflow | Trigger | Responsibilities |
|---|---|---|
| `progress.yml` | Push to `main` in the **upstream** repository | Validate `PROJECT_PLAN.md`, compute progress, milestones and commit activity, regenerate `assets/status/*.svg`, refresh the README between the `PROGRESS` and `MILESTONES` markers, commit only if something changed |
| `pr-checks.yml` | Pull request opened, synchronized or reopened | Validate the tracking contract, lint and format check, run all tests (`scripts/tests`, `platform/server/tests`, `contracts/tests`), build the dashboard when `platform/dashboard/` changed |

A mobile job will be added to `pr-checks.yml` by task MOB-01, when the Android project exists.

## Metrics

- **Actual progress** = done tasks with priority P0/P1 ÷ all P0/P1 tasks.
- **Optional progress** (P2) is shown separately.
- **Milestone complete** = all of its core tasks are done **and** every exit gate is ticked. Milestone M8 (optional) uses its optional tasks and is excluded from the headline.
- **Commit activity** is a separate metric and never completes a task. Commits whose message starts with `chore(status):` are excluded from the count.

## Engineering rules

1. **No loops.** The generated commit contains `[skip ci]`, the job skips the bot's own commits, `paths-ignore` excludes `README.md` and `assets/status/**`, and pushes made with the default token do not trigger workflows.
2. **Minimal permissions.** `contents: read` by default; `contents: write` only for the status job.
3. **Forks.** The status job runs only when the repository is not a fork. Pull requests from forks run read-only checks with no secrets.
4. **No secrets.** Neither workflow uses secrets.
5. **Failure handling.** If `PROJECT_PLAN.md` violates the tracking contract the job fails with line references and the README is left unchanged. If the push is rejected because `main` moved, the job fails and the next push regenerates the files.
6. **Local dry runs.** `python scripts/update_status.py --validate`, `--dry-run` and `--write` behave exactly like the workflow steps.
7. **Later dependency.** If branch protection is enabled later, the status job will need an explicit bypass or a dedicated credential.

## Validation status

| Item | Generated | Syntax-validated | Locally tested | Tested on GitHub |
|---|---|---|---|---|
| Tracking parser, metrics, SVG generator, README sync | yes | yes (ruff) | yes (pytest) | no |
| `progress.yml` | yes | yes (YAML parse, actionlint) | steps run locally; the workflow itself was not run | no |
| `pr-checks.yml` | yes | yes (YAML parse, actionlint) | commands run locally; the workflow itself was not run | no |
