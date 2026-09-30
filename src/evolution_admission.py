"""Local admission gate for verified evolutionary commits."""

from __future__ import annotations

from dataclasses import dataclass

from src.commit import EvolutionCommit
from src.evolution_history import EvolutionHistoryAudit


@dataclass(frozen=True)
class EvolutionAdmission:
    admissible: bool
    candidate_id: str
    current_state_id: str
    convergence_id: str
    reason: str
    version: int = 1


def admit_evolution(
    candidate_commit: EvolutionCommit,
    history_audit: EvolutionHistoryAudit,
    current_state_id: str,
    expected_convergence_id: str,
) -> EvolutionAdmission:
    if not isinstance(candidate_commit, EvolutionCommit):
        raise TypeError("candidate_commit must be an EvolutionCommit")
    if not isinstance(history_audit, EvolutionHistoryAudit):
        raise TypeError("history_audit must be an EvolutionHistoryAudit")

    if not isinstance(current_state_id, str) or not current_state_id.strip():
        raise ValueError("current_state_id must be non-empty")
    if (
        not isinstance(expected_convergence_id, str)
        or not expected_convergence_id.strip()
    ):
        raise ValueError("expected_convergence_id must be non-empty")

    if not history_audit.valid:
        return EvolutionAdmission(
            admissible=False,
            candidate_id=candidate_commit.id,
            current_state_id=current_state_id,
            convergence_id=candidate_commit.convergence_id,
            reason="history_audit_invalid",
        )

    if candidate_commit.previous_state_id != current_state_id:
        return EvolutionAdmission(
            admissible=False,
            candidate_id=candidate_commit.id,
            current_state_id=current_state_id,
            convergence_id=candidate_commit.convergence_id,
            reason="state_mismatch",
        )

    if candidate_commit.convergence_id != expected_convergence_id:
        return EvolutionAdmission(
            admissible=False,
            candidate_id=candidate_commit.id,
            current_state_id=current_state_id,
            convergence_id=candidate_commit.convergence_id,
            reason="convergence_mismatch",
        )

    return EvolutionAdmission(
        admissible=True,
        candidate_id=candidate_commit.id,
        current_state_id=current_state_id,
        convergence_id=candidate_commit.convergence_id,
        reason="admitted",
    )


__all__ = ["EvolutionAdmission", "admit_evolution"]
