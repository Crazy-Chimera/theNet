from dataclasses import FrozenInstanceError

import pytest

from src.iota import Singularity, create_singularity


VALUES = {
    "phi_id": "phi",
    "omega_id": "omega",
    "omega2_id": "omega2",
    "resonance_id": "resonance",
    "gamma_id": "gamma",
    "pi_id": "pi",
    "psi_id": "psi",
    "theta_id": "theta",
    "rho_id": "rho",
    "sigma_id": "sigma",
    "created_at": "2026-09-22T00:00:00Z",
}


def test_iota_closes_all_architectural_layers():
    state = create_singularity(**VALUES)

    assert isinstance(state, Singularity)
    assert state.phi_id == "phi"
    assert state.sigma_id == "sigma"


def test_iota_identity_is_deterministic():
    assert create_singularity(**VALUES) == create_singularity(**VALUES)


def test_changing_any_layer_changes_identity():
    first = create_singularity(**VALUES)
    changed = {**VALUES, "rho_id": "rho-2"}

    assert first.id != create_singularity(**changed).id


def test_missing_required_value_is_rejected():
    invalid = {**VALUES, "sigma_id": ""}
    with pytest.raises(ValueError):
        create_singularity(**invalid)


def test_iota_is_immutable():
    state = create_singularity(**VALUES)
    with pytest.raises(FrozenInstanceError):
        state.version = 2
