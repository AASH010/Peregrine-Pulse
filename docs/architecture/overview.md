# Architecture overview

Direction only; decisions and tasks live in [`PROJECT_PLAN.md`](../../PROJECT_PLAN.md).

```
 Phone (mobile/)                                        Cloud (platform/ on Huawei Cloud)
 ┌──────────────────────────┐   Wi-Fi / mobile network  ┌─────────────────────────────────────┐
 │ :android  sensors, UI,   │ ────────────────────────► │ API → Orchestrator → Registry       │
 │           transports     │                           │       (policy, planner, tools)      │
 │ :core     risk rules,    │   satellite (rented       │ Satellite Gateway (provider adapter)│◄── provider ground segment
 │           capability,    │   service; SIMULATED)     │ Notification service (SIMULATED)    │    (or Simulated Satellite Link)
 │           ladder, queue  │ ────────────────────────► │ RDS: incidents, trace, registry     │
 └──────────────────────────┘                           └───────────────┬─────────────────────┘
        ▲ optional: BLE/USB ◄── hardware/ (ESP32 module emulator)       │ feed
                                                                        ▼
                                                              Dashboard (platform/dashboard)
```

## Principles
- **Evidence over assumption:** a lifecycle stage is shown only when its evidence exists (`contracts/states/transitions.json`).
- **Model proposes, policy decides:** any AI suggestion passes a deterministic policy gate.
- **Simulated is labelled:** every simulated path, entity or notification carries a visible SIMULATED marker.
- **The rescue agent and the AI development assistants are separate systems.**

## Connectivity ladder
Default order Wi-Fi → mobile network → satellite, as a configurable policy. Each path is probed for real reachability. Every path implements one `Transport` interface (real, simulated or hardware). Tier 1 information is sent first. With no path at all the incident stays *Queued*.

## Satellite path
Rented third-party service (provider TBD). The cloud-side **Satellite Gateway** verifies the source, rejects replays and oversize messages, decodes the compact payload, stores before triggering the orchestrator, and returns only a technical receipt. Initial experiments use a **Simulated Satellite Link** (configurable latency, size limit, loss, duplication, reordering, availability windows). An optional ESP32 module emulator makes the device-side interface real while the radio stays simulated.

## State model
Internal states drive the server and the agent. People see seven stages — Prepared, Sent, Delivered, Acknowledged, Response Dispatched, Arrived, Closed — plus overlays (Queued, Escalating, Cancelled, Not handled). See `contracts/states/transitions.json` and its tests.
