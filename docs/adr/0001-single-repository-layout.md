# 0001 — Single repository with area folders

- **Status:** Accepted
- **Date:** 2026-11-21
- **Related tasks:** OPS-01, LIF-05

## Context
The project has a mobile app, a cloud platform with a dashboard, optional hardware, shared contracts and a single plan whose status drives the README. Members work through forks.

## Options considered
1. **One repository with folders** (`mobile/`, `platform/`, `hardware/`, `contracts/`, `docs/`) — one history, one automation, contracts shared in one place; areas separated by path and by branch prefix.
2. **Permanent branches per area** (for example `main`, `mobile`, `platform`) — separate histories; the generated README and the workflows would have to exist and stay in sync on every branch; contracts would be duplicated; merges become painful.

## Decision
Option 1. Work branches are prefixed by area (`mobile/…`, `platform/…`, `hardware/…`, `docs/…`). CI filters by path where useful.

## Consequences
One place for contracts and the plan; progress automation works on a single branch; the mobile and platform areas must still keep changes small to avoid conflicts in shared files.
