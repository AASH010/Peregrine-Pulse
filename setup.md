# Development Setup

This file covers everything needed to work on the repository **as it exists today**: the platform server skeleton, the dashboard skeleton, the contracts and the tracking scripts. The Android project does not exist yet (task MOB-01), and nothing is deployed to the cloud yet (concept C11).

Commands below were run on Linux. Values marked **(owner)** must be supplied by the project owner. Never commit real secrets, tokens or passwords.

## 1. Prerequisites
- A GitHub account and a fork of the upstream repository (work happens through forks).
- A terminal with Bash (Linux or macOS; Windows users can use WSL).

## 2. Required Software
| Software | Used for |
|---|---|
| Git | Version control |
| Python | Platform server, tracking scripts, tests |
| Node.js and npm | Dashboard |
| Android Studio | **Not needed yet.** Required from task MOB-01 |
| Huawei Cloud account | **Not needed yet.** Required from M4 (see section 9) |

## 3. Required Versions
| Software | Version used for validation |
|---|---|
| Python | 3.12 (tested with 3.12.3) |
| Node.js | 22 (tested with v22.23.5) |
| npm | 10 (tested with 10.9.9) |
| Git | any recent version (tested with 2.43.0) |

Python and npm dependency versions are pinned in `requirements-dev.txt`, `platform/server/requirements.txt` and `platform/dashboard/package-lock.json`.

## 4. Repository Setup
```bash
git clone <your-fork-url> PeregrinePulse        # (owner/member) the URL of your fork
cd PeregrinePulse
git remote add upstream <upstream-repository-url>  # (owner) the URL of the main repository
git checkout -b platform/my-change              # branch prefixes: mobile/, platform/, hardware/, docs/
```

## 5. Installation
```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

cd platform/dashboard
npm ci
cd ../..
```
Use the virtual environment: installing into the system Python can fail with an "externally-managed-environment" error.

## 6. Environment Variables
The platform server reads the **process environment**. Variables are defined in `.env.example`:

| Variable | Default | Meaning |
|---|---|---|
| `PP_ENV` | `development` | `development` or `production` |
| `PP_API_HOST` | `127.0.0.1` | Address the API binds to (used when you pass it to `uvicorn`, see section 10) |
| `PP_API_PORT` | `8000` | Port the API binds to (integer, 1–65535) |
| `PP_CORS_ORIGINS` | `http://localhost:5173` | Comma-separated origins allowed to call the API |
| `PP_DATABASE_URL` | *(empty)* | MySQL URL — **(owner)** supplies it once the database exists (tasks API-02, CLD-03). Empty is fine for the skeleton |

## 7. `.env.example` Configuration
```bash
cp .env.example .env          # .env is git-ignored
set -a; source .env; set +a   # load the variables into the current shell
```

## 8. Database Setup
No database is used yet. The schema and migrations arrive with task API-02, and the managed database (Huawei Cloud RDS for MySQL) with CLD-03. Until then leave `PP_DATABASE_URL` empty.

## 9. External Services Configuration
Nothing external is required to run what exists today. Later, the **(owner)** supplies:

- **Huawei Cloud:** account access, region, quotas and credits, and confirmation that ECS and RDS for MySQL (and DCS for Redis, if used) are available in that region. Complete the readiness checklist in `cloud/README.md` first. Credentials are provided through the environment or a secret store, never in the repository.
- **Satellite provider:** not selected (research task SAT-01). The initial experiments use a simulated link, so no account is needed.

## 10. Running the Project Locally
Platform server (from the repository root, with the virtual environment active and the variables loaded):
```bash
cd platform/server
uvicorn app.main:app --host "${PP_API_HOST:-127.0.0.1}" --port "${PP_API_PORT:-8000}"
```
Check it from another terminal:
```bash
curl http://127.0.0.1:8000/health          # {"status":"ok"}
curl http://127.0.0.1:8000/api/v1/meta
```
Interactive API documentation is served at `http://127.0.0.1:8000/docs`.

Dashboard:
```bash
cd platform/dashboard
npm run dev                                 # http://localhost:5173
```
The Android app cannot be run yet (see `mobile/README.md`).

## 11. Running Tests
From the repository root with the virtual environment active:
```bash
python -m pytest                            # tracking scripts, platform server, contracts
ruff check .
ruff format --check .
python scripts/update_status.py --validate  # PROJECT_PLAN.md tracking contract
cd platform/dashboard && npm run build      # dashboard build check
```

## 12. Development Commands
| Command | Purpose |
|---|---|
| `python scripts/update_status.py --validate` | Check `PROJECT_PLAN.md` against the tracking contract |
| `python scripts/update_status.py --dry-run` | Print computed progress, milestones and commit activity as JSON; writes nothing |
| `python scripts/update_status.py --write` | Regenerate `assets/status/*.svg` and the README progress and milestone sections |
| `ruff format .` | Format Python code |
| `python -m pytest contracts/tests` | Run only the contract tests |

The README progress and milestone sections are refreshed automatically on `main` (see `docs/workflows.md`). Run `--write` locally only to preview, and do not commit its output on feature branches. When you finish a task, set its status to `done` in `PROJECT_PLAN.md` in the same pull request. Commit and pull request standards are in `docs/contributing.md`.

## 13. Troubleshooting
| Symptom | Likely cause and fix |
|---|---|
| `externally-managed-environment` when running `pip install` | Install inside the virtual environment (section 5) |
| `ModuleNotFoundError: No module named 'app'` | Run `pytest` from the repository root (`pytest.ini` sets the path), or run `uvicorn` from `platform/server` |
| `PP_API_PORT must be an integer` | Fix the value in `.env` and reload it (section 7) |
| Port already in use | Change `PP_API_PORT`, or stop the other process |
| `update_status.py` fails with `line N: …` | The plan violates the tracking contract; fix the cited row (IDs, dependencies, statuses, column count) |
| `README markers for PROGRESS not found` | Restore the `<!-- PROGRESS:START -->` and `<!-- PROGRESS:END -->` comments in `README.md` |
| `npm ci` fails because the lock file is out of sync | Run `npm install` in `platform/dashboard` and commit the updated `package-lock.json` |

## 14. Common Setup Problems
- **Dashboard cannot reach the API:** make sure the server is running and `PP_CORS_ORIGINS` includes the dashboard origin (`http://localhost:5173` by default).
- **A folder named `platform/` shadows nothing:** it has no `__init__.py` on purpose; do not add one, because Python's standard library also has a `platform` module.
- **Tests pass locally but a pull request fails:** the pull request checks run `ruff check .` and `ruff format --check .` in addition to the tests; run both before pushing.
