"""Immutable archive records for reproducible counterfactual experiments."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from src.counterfactual_experiment_matrix import CounterfactualExperimentMatrix
from src.counterfactual_reproducibility import ExperimentFingerprint


@dataclass(frozen=True)
class ExperimentLedgerRecord:
    id: str
    fingerprint: ExperimentFingerprint
    matrix: CounterfactualExperimentMatrix
    created_at: str
    version: int = 1

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "fingerprint": self.fingerprint.as_dict(),
            "matrix": self.matrix.as_dict(),
            "created_at": self.created_at,
            "version": self.version,
        }


def create_experiment_ledger_record(
    *,
    matrix: CounterfactualExperimentMatrix,
    fingerprint: ExperimentFingerprint,
    created_at: str,
) -> ExperimentLedgerRecord:
    if not isinstance(matrix, CounterfactualExperimentMatrix):
        raise TypeError("matrix must be CounterfactualExperimentMatrix")
    if not isinstance(fingerprint, ExperimentFingerprint):
        raise TypeError("fingerprint must be ExperimentFingerprint")
    if not isinstance(created_at, str) or not created_at.strip():
        raise ValueError("created_at must be non-empty")

    identifier = fingerprint.result_fingerprint
    return ExperimentLedgerRecord(
        id=identifier,
        fingerprint=fingerprint,
        matrix=matrix,
        created_at=created_at,
    )


__all__ = ["ExperimentLedgerRecord", "create_experiment_ledger_record"]
