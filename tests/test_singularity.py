from dataclasses import FrozenInstanceError

import pytest

from src.singularity import create_singularity


BASE = (
    "phi",
    "omega",
    "omega2",
    "resonance",
    "gamma",
    "pi",
    "psi",
    "theta",
    "rho",
    "sigma",
    "2026-09-21T00:00:00Z",
)


def test_create_singularity():
    item = create_singularity(*BASE)

    assert item.phi_id == "phi"
    assert item.omega_id == "omega"
    assert item.sigma_id == "sigma"
    assert item.created_at == BASE[-1]
    assert item.version == 1
    assert len(item.id) == 64


def test_identity_is_deterministic():
    assert create_singularity(*BASE).id == create_singularity(*BASE).id


@pytest.mark.parametrize("index", range(len(BASE)))
def test_empty_defining_input_is_rejected(index):
    values = list(BASE)
    values[index] = "   "

    with pytest.raises(ValueError):
        create_singularity(*values)


def test_non_string_input_is_rejected():
    values = list(BASE)
    values[3] = None

    with pytest.raises(ValueError):
        create_singularity(*values)


def test_result_is_immutable():
    item = create_singularity(*BASE)

    with pytest.raises(FrozenInstanceError):
        item.phi_id = "other"


@pytest.mark.parametrize("index", range(10))
def test_changing_any_layer_changes_identity(index):
    values = list(BASE)
    values[index] = values[index] + "-changed"

    assert create_singularity(*values).id != create_singularity(*BASE).id


def test_timestamp_changes_identity():
    values = list(BASE)
    values[-1] = "2026-09-22T00:00:00Z"

    assert create_singularity(*values).id != create_singularity(*BASE).id
