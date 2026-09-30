from dataclasses import FrozenInstanceError

import pytest

from src.agent import run_decision_cycle
from src.agent_state import create_agent_state
from src.genesis import create_genesis
from src.identity import IdentityVault
from src.proposal import create_proposal
from src.relation import create_relation


STAMP = "2026-09-30T00:00:00Z"


def _inputs(tmp_path=None):
    source = create_genesis("agent:a", STAMP)
    target = create_genesis("agent:b", STAMP)
    state = create_agent_state(source.id, "singularity:a", STAMP)
    proposal = create_proposal(
        source.id,
        state.id,
        "advance verified relational state",
        STAMP,
    )
    relation = create_relation(source.id, target.id, "supports", STAMP)
    return state, proposal, [relation]


def test_decision_cycle_has_required_order_and_all_stages(tmp_path):
    state, proposal, relations = _inputs(tmp_path)
    cycle = run_decision_cycle(state, proposal, relations, STAMP)

    assert cycle.order == ("THETA", "SIGMA", "GAMMA", "OMEGA", "PI", "OMEGA2")
    assert cycle.theta.subject_id == state.subject_id
    assert cycle.sigma.relation_ids == (relations[0].id,)
    assert cycle.gamma.resolved_id == proposal.id
    assert cycle.omega.from_state == state.id
    assert cycle.pi.convergence_id == cycle.gamma.id
    assert cycle.omega2.transition_id == cycle.omega.id


def test_decision_cycle_is_side_effect_free_for_canonical_state(tmp_path):
    state, proposal, relations = _inputs(tmp_path)

    cycle = run_decision_cycle(state, proposal, relations, STAMP)

    assert cycle.omega.from_state == state.id
    assert state.version == 1


def test_decision_cycle_binds_verified_identity(tmp_path):
    state, proposal, relations = _inputs(tmp_path)
    vault = IdentityVault(tmp_path / "vault.json")
    identity = vault.create("password")

    # Proposal identity is represented by the deterministic DID.
    proposal = create_proposal(
        identity.did,
        state.id,
        proposal.proposal,
        STAMP,
    )

    cycle = run_decision_cycle(
        state,
        proposal,
        relations,
        STAMP,
        identity=identity,
        vault=vault,
        password="password",
    )

    assert cycle.proposal_signature is not None
    assert cycle.identity_verified is True


def test_invalid_proposal_target_is_rejected(tmp_path):
    state, proposal, relations = _inputs(tmp_path)
    other = create_genesis("other", STAMP)
    proposal = create_proposal(
        state.subject_id,
        other.id,
        "wrong base",
        STAMP,
    )

    with pytest.raises(ValueError, match="current state"):
        run_decision_cycle(state, proposal, relations, STAMP)


def test_empty_relations_are_rejected(tmp_path):
    state, proposal, _ = _inputs(tmp_path)

    with pytest.raises(ValueError, match="at least one relation"):
        run_decision_cycle(state, proposal, [], STAMP)


def test_cycle_is_immutable(tmp_path):
    state, proposal, relations = _inputs(tmp_path)
    cycle = run_decision_cycle(state, proposal, relations, STAMP)

    with pytest.raises(FrozenInstanceError):
        cycle.order = ()
