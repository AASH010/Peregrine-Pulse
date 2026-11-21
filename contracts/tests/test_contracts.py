"""Contract tests: schemas are valid, fixtures behave, and the state model is consistent."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

CONTRACTS = Path(__file__).resolve().parents[1]


def load(relative: str) -> dict:
    return json.loads((CONTRACTS / relative).read_text(encoding="utf-8"))


INCIDENT = load("incident/incident.schema.json")
TIER1 = load("payload/tier1.schema.json")
STATES = load("states/transitions.json")


@pytest.mark.parametrize("schema", [INCIDENT, TIER1])
def test_schemas_are_valid(schema):
    Draft202012Validator.check_schema(schema)


@pytest.mark.parametrize(
    "schema,fixture",
    [(INCIDENT, "fixtures/valid_incident.json"), (TIER1, "fixtures/valid_tier1.json")],
)
def test_valid_fixtures_pass(schema, fixture):
    errors = list(Draft202012Validator(schema).iter_errors(load(fixture)))
    assert errors == []


@pytest.mark.parametrize(
    "schema,fixture",
    [
        (INCIDENT, "fixtures/invalid_incident_missing_location.json"),
        (INCIDENT, "fixtures/invalid_incident_bad_confidence.json"),
        (INCIDENT, "fixtures/invalid_incident_simulated_not_boolean.json"),
        (TIER1, "fixtures/invalid_tier1_missing_sequence.json"),
        (TIER1, "fixtures/invalid_tier1_no_distress.json"),
    ],
)
def test_invalid_fixtures_fail(schema, fixture):
    assert list(Draft202012Validator(schema).iter_errors(load(fixture)))


def test_timestamps_must_look_like_rfc3339():
    incident = load("fixtures/valid_incident.json")
    incident["detected_at"] = "yesterday"
    assert list(Draft202012Validator(INCIDENT).iter_errors(incident))


def test_every_state_is_a_stage_or_an_overlay_exactly_once():
    transitions = set(STATES["transitions"])
    stage_states, overlay_states = set(STATES["stage_map"]), set(STATES["overlay_map"])
    assert stage_states | overlay_states == transitions
    assert not stage_states & overlay_states


def test_stage_map_uses_only_declared_stages_and_all_are_reachable():
    declared = set(STATES["stages"])
    assert set(STATES["stage_map"].values()) <= declared
    assert set(STATES["stage_map"].values()) == declared
    assert set(STATES["evidence_required"]) == declared


def test_transitions_reference_known_states_only():
    known = set(STATES["transitions"])
    for source, targets in STATES["transitions"].items():
        assert set(targets) <= known, source
    assert STATES["initial"] in known
    assert set(STATES["terminal"]) <= known


def test_terminal_states_have_no_outgoing_transitions_and_others_do():
    for state, targets in STATES["transitions"].items():
        assert (state in STATES["terminal"]) == (not targets), state


def _reachable(start: str) -> set[str]:
    seen, stack = set(), [start]
    while stack:
        node = stack.pop()
        if node not in seen:
            seen.add(node)
            stack.extend(STATES["transitions"][node])
    return seen


def test_every_state_is_reachable_from_the_initial_state():
    assert _reachable(STATES["initial"]) == set(STATES["transitions"])


def test_every_state_can_reach_a_terminal_state():
    terminal = set(STATES["terminal"])
    for state in STATES["transitions"]:
        assert _reachable(state) & terminal, state


def test_delivered_is_only_reachable_from_sending():
    sources = [s for s, t in STATES["transitions"].items() if "AWAITING_ACK" in t]
    assert sources == ["SENDING"]


def test_acknowledgment_is_only_reachable_from_awaiting_ack():
    sources = [s for s, t in STATES["transitions"].items() if "ACKNOWLEDGED" in t]
    assert sources == ["AWAITING_ACK"]
