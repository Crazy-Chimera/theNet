from dataclasses import FrozenInstanceError

import pytest

from src.pi import create_meaning


def test_meaning_records_convergence_and_contribution():
    result = create_meaning(
        "convergence:a",
        "contribution:b",
        "2026-09-22T00:00:00Z",
    )

    assert result.convergence_id == "convergence:a"
    assert result.contribution_id == "contribution:b"
    assert len(result.id) == 64
    assert result.version == 1


def test_meaning_identity_is_deterministic():
    left = create_meaning("convergence:a", "contribution:b", "2026-09-22T00:00:00Z")
    right = create_meaning("convergence:a", "contribution:b", "2026-09-22T00:00:00Z")

    assert left == right


@pytest.mark.parametrize(
    "convergence_id, contribution_id, created_at",
    [
        ("", "contribution:b", "2026-09-22T00:00:00Z"),
        ("convergence:a", "", "2026-09-22T00:00:00Z"),
        ("convergence:a", "contribution:b", ""),
        (None, "contribution:b", "2026-09-22T00:00:00Z"),
    ],
)
def test_meaning_rejects_invalid_inputs(
    convergence_id,
    contribution_id,
    created_at,
):
    with pytest.raises(ValueError):
        create_meaning(convergence_id, contribution_id, created_at)


def test_meaning_changes_when_contribution_changes():
    left = create_meaning("convergence:a", "contribution:a", "2026-09-22T00:00:00Z")
    right = create_meaning("convergence:a", "contribution:b", "2026-09-22T00:00:00Z")

    assert left.id != right.id


def test_meaning_changes_when_convergence_changes():
    left = create_meaning("convergence:a", "contribution:b", "2026-09-22T00:00:00Z")
    right = create_meaning("convergence:b", "contribution:b", "2026-09-22T00:00:00Z")

    assert left.id != right.id


def test_meaning_is_immutable():
    result = create_meaning("convergence:a", "contribution:b", "2026-09-22T00:00:00Z")

    with pytest.raises(FrozenInstanceError):
        result.contribution_id = "changed"
