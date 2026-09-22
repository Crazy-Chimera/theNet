"""Canonical ΙΩΤΑ unity entry point for theNet."""

from __future__ import annotations

from src.singularity import Singularity, create_singularity as _create_singularity


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
    """Build the canonical immutable ΙΩΤΑ architectural closure."""
    return _create_singularity(
        phi_id,
        omega_id,
        omega2_id,
        resonance_id,
        gamma_id,
        pi_id,
        psi_id,
        theta_id,
        rho_id,
        sigma_id,
        created_at,
    )


__all__ = ["Singularity", "create_singularity"]
