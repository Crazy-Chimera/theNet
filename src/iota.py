"""Minimal immutable ΙΩΤΑ architectural unity closure for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class Singularity:
    id: str
    phi_id: str
    omega_id: str
    omega2_id: str
    resonance_id: str
    gamma_id: str
    pi_id: str
    psi_id: str
    theta_id: str
    rho_id: str
    sigma_id: str
    created_at: str
    version: int = 1


def _canonical(values: dict[str, str]) -> str:
    return json.dumps(
        {**values, "version": 1},
        sort_keys=True,
        separators=(",", ":"),
    )


def create_singularity(
    phi_id: str,
    omega_id: str,
    omega2_id: str,
    resonance_id: str,
    gamma_id: str,
    pi_id: str,
    psi_id: str,
    theta_id: str,
    rho_id: str,
    sigma_id: str,
    created_at: str,
) -> Singularity:
    values = {
        "phi_id": phi_id,
        "omega_id": omega_id,
        "omega2_id": omega2_id,
        "resonance_id": resonance_id,
        "gamma_id": gamma_id,
        "pi_id": pi_id,
        "psi_id": psi_id,
        "theta_id": theta_id,
        "rho_id": rho_id,
        "sigma_id": sigma_id,
        "created_at": created_at,
    }

    for name, value in values.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be non-empty")

    identifier = sha256(_canonical(values).encode("utf-8")).hexdigest()

    return Singularity(id=identifier, **values)


__all__ = ["Singularity", "create_singularity"]
