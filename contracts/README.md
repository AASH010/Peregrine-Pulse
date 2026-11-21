# contracts/

Shared, versioned schemas used by the mobile app, the platform, the dashboard and the experiments. **Draft v0.1.0** — these files are a starting point for tasks LIF-01 to LIF-04 and are reviewed by the whole team before any task is marked done.

| Path | Purpose | Task |
|---|---|---|
| `incident/incident.schema.json` | Canonical Incident Object | LIF-01 |
| `payload/tier1.schema.json` | Tier 1 critical payload (wire encoding and byte budget decided after SAT-01) | LIF-02 |
| `states/transitions.json` | Two-layer state model: internal states, user-facing stages, overlays, evidence per stage | LIF-03, LIF-04 |
| `fixtures/` | Valid and invalid examples used by the tests | — |
| `tests/test_contracts.py` | Schema validity, fixture behaviour, state-model consistency | — |

**Rules**
- A stage is shown only when its evidence exists. A gateway or relay receipt (`service_received`) is never displayed as *Delivered* or *Acknowledged*.
- Every incident carries a `simulated` flag; simulated data must never be presented as real.
- Contract changes bump the version and need review from every team member.

Run the tests from the repository root: `python -m pytest contracts/tests` (see `setup.md`).
