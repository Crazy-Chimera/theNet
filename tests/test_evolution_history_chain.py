from dataclasses import FrozenInstanceError

import pytest

from src.evolution_history_chain import (
    EvolutionHistoryChain,
    create_evolution_history_chain,
)
from src.evolution_history_root_anchor import create_evolution_history_root_anchor


STAMP = "2026-09-30T00:00:00Z"


def make_anchor(current: str, previous: str | None = None):
    return create_evolution_history_root_anchor(current, STAMP, previous)


def test_single_first_epoch_anchor_forms_chain():
    chain = create_evolution_history_chain([make_anchor("root-1")])

    assert isinstance(chain, EvolutionHistoryChain)
    assert chain.anchor_ids == (make_anchor("root-1").id,)
    assert chain.root_ids == ("root-1",)
    assert chain.length == 1


def test_multiple_anchors_form_continuous_chain():
    first = make_anchor("root-1")
    second = make_anchor("root-2", "root-1")
    third = make_anchor("root-3", "root-2")

    chain = create_evolution_history_chain([first, second, third])

    assert chain.anchor_ids == (first.id, second.id, third.id)
    assert chain.root_ids == ("root-1", "root-2", "root-3")
    assert chain.length == 3


def test_chain_identity_is_deterministic():
    left = [
        make_anchor("root-1"),
        make_anchor("root-2", "root-1"),
    ]
    right = [
        make_anchor("root-1"),
        make_anchor("root-2", "root-1"),
    ]

    assert create_evolution_history_chain(left) == create_evolution_history_chain(right)


def test_empty_chain_is_rejected():
    with pytest.raises(ValueError):
        create_evolution_history_chain([])


def test_invalid_anchor_type_is_rejected():
    with pytest.raises(TypeError):
        create_evolution_history_chain([object()])


def test_first_anchor_must_be_chain_root():
    with pytest.raises(ValueError):
        create_evolution_history_chain([make_anchor("root-2", "root-1")])


def test_broken_continuity_is_rejected():
    anchors = [
        make_anchor("root-1"),
        make_anchor("root-2", "root-1"),
        make_anchor("root-3", "root-x"),
    ]

    with pytest.raises(ValueError):
        create_evolution_history_chain(anchors)


def test_reordering_is_rejected_when_continuity_breaks():
    anchors = [
        make_anchor("root-1"),
        make_anchor("root-2", "root-1"),
    ]

    with pytest.raises(ValueError):
        create_evolution_history_chain(list(reversed(anchors)))


def test_chain_is_immutable():
    chain = create_evolution_history_chain([make_anchor("root-1")])

    with pytest.raises(FrozenInstanceError):
        chain.version = 2


def test_input_sequence_is_not_mutated():
    anchors = [make_anchor("root-1"), make_anchor("root-2", "root-1")]

    create_evolution_history_chain(anchors)

    assert len(anchors) == 2
    assert anchors[0].current_root_id == "root-1"
    assert anchors[1].previous_root_id == "root-1"


def test_distinct_chain_changes_identity():
    first = create_evolution_history_chain(
        [make_anchor("root-1"), make_anchor("root-2", "root-1")]
    )
    second = create_evolution_history_chain(
        [make_anchor("root-1"), make_anchor("root-3", "root-1")]
    )

    assert first.id != second.id
