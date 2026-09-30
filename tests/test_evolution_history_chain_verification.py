from dataclasses import FrozenInstanceError

import pytest

from src.evolution_history_chain import create_evolution_history_chain
from src.evolution_history_chain_verification import (
    EvolutionHistoryChainVerification,
    verify_evolution_history_chain,
)
from src.evolution_history_root_anchor import create_evolution_history_root_anchor


STAMP = "2026-09-30T00:00:00Z"


def make_anchor(current: str, previous: str | None = None, stamp: str = STAMP):
    return create_evolution_history_root_anchor(current, stamp, previous)


def test_matching_chain_is_valid():
    anchors = [make_anchor("root-1"), make_anchor("root-2", "root-1")]
    chain = create_evolution_history_chain(anchors)

    result = verify_evolution_history_chain(anchors, chain)

    assert isinstance(result, EvolutionHistoryChainVerification)
    assert result.valid is True
    assert result.expected_chain_id == chain.id
    assert result.provided_chain_id == chain.id
    assert result.error is None


def test_changed_anchor_is_invalid():
    anchors = [make_anchor("root-1"), make_anchor("root-2", "root-1")]
    chain = create_evolution_history_chain(anchors)
    changed = [make_anchor("root-1"), make_anchor("root-3", "root-1")]

    result = verify_evolution_history_chain(changed, chain)

    assert result.valid is False
    assert result.error == "chain does not match supplied anchors"


def test_reordered_chain_is_invalid():
    anchors = [make_anchor("root-1"), make_anchor("root-2", "root-1")]
    chain = create_evolution_history_chain(anchors)

    result = verify_evolution_history_chain(list(reversed(anchors)), chain)

    assert result.valid is False


def test_broken_anchor_sequence_is_invalid():
    anchors = [
        make_anchor("root-1"),
        make_anchor("root-2", "root-1"),
        make_anchor("root-3", "root-x"),
    ]
    valid_chain = create_evolution_history_chain(
        [make_anchor("root-1"), make_anchor("root-2", "root-1")]
    )

    result = verify_evolution_history_chain(anchors, valid_chain)

    assert result.valid is False
    assert result.expected_chain_id is None
    assert "continuous" in result.error


def test_empty_anchor_sequence_is_invalid():
    chain = create_evolution_history_chain([make_anchor("root-1")])

    result = verify_evolution_history_chain([], chain)

    assert result.valid is False
    assert result.expected_chain_id is None


def test_wrong_chain_type_is_rejected():
    with pytest.raises(ValueError, match="EvolutionHistoryChain"):
        verify_evolution_history_chain([], object())


def test_invalid_anchor_type_is_invalid():
    chain = create_evolution_history_chain([make_anchor("root-1")])

    result = verify_evolution_history_chain([object()], chain)

    assert result.valid is False
    assert result.expected_chain_id is None


def test_verification_is_deterministic():
    anchors = [make_anchor("root-1"), make_anchor("root-2", "root-1")]
    chain = create_evolution_history_chain(anchors)

    left = verify_evolution_history_chain(anchors, chain)
    right = verify_evolution_history_chain(list(anchors), chain)

    assert left == right


def test_inputs_and_chain_are_not_mutated():
    anchors = [make_anchor("root-1"), make_anchor("root-2", "root-1")]
    original = list(anchors)
    chain = create_evolution_history_chain(anchors)

    verify_evolution_history_chain(anchors, chain)

    assert anchors == original
    assert chain == create_evolution_history_chain(original)


def test_result_is_immutable():
    anchors = [make_anchor("root-1")]
    chain = create_evolution_history_chain(anchors)
    result = verify_evolution_history_chain(anchors, chain)

    with pytest.raises(FrozenInstanceError):
        result.valid = False
