# Contributing

Two standards apply to every change: the **commit convention** and the **pull request template**. Work happens through forks; branches are prefixed by area (`mobile/…`, `platform/…`, `hardware/…`, `docs/…`).

## Commit convention

Format: `type(scope): short imperative summary`, with an optional body and footer.

```
feat(mobile): add offline queue persistence
fix(platform): reject replayed acknowledgment

Refs: NET-04
```

**Types:** `feat` new capability · `fix` bug fix · `docs` documentation · `style` formatting only · `refactor` no behaviour change · `test` tests only · `perf` performance · `build` build or dependencies · `ci` workflows · `chore` maintenance.

**Scopes:** `mobile`, `platform`, `dashboard`, `hardware`, `contracts`, `experiments`, `data`, `cloud`, `docs`, `plan`, `ops`.

**Rules**
- Imperative mood; summary up to about 72 characters.
- Explain *why* in the body when it is not obvious.
- One logical change per commit.
- Mention task IDs in a `Refs:` footer.
- Mark breaking contract changes with `!` (for example `feat(contracts)!: rename stage`) and a `BREAKING CHANGE:` footer.
- A task is finished by editing its status in `PROJECT_PLAN.md` in the same pull request (`docs(plan): mark LIF-03 done`), not by the commit message alone.
- `chore(status): …` commits are reserved for the automation (see `workflows.md`).

| Correct | Incorrect |
|---|---|
| `fix(platform): ignore duplicate incident ids` | `fixed stuff` |
| `feat(mobile): show Queued overlay when offline` | `Added the feature of offline.` |
| `docs(plan): mark SEC-01 done` | `update` |
| `test(contracts): cover illegal state transitions` | `tests and some refactoring and docs` |

## Pull request template

The template lives in [`.github/pull_request_template.md`](../.github/pull_request_template.md) and is applied automatically. It covers: title, description, purpose, related tasks, implemented changes, testing, documentation updates, potential breaking changes, integration considerations and the completion checklist.
