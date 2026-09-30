"""Immutable archive records for reproducible counterfactual experiments."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json

from src.counterfactual_experiment_matrix import CounterfactualExperimentMatrix
from src.counterfactual_reproducibility import ExperimentFingerprint


@dataclass(frozen=True)
class ExperimentLedgerRecord:
    id: str
    run_id: str
    fingerprint: ExperimentFingerprint
    matrix: CounterfactualExperimentMatrix
    created_at: str
    version: int = 2

    def as_dict(self) -> dict:
        return asdict(self)


def create_experiment_ledger_record(
    *,
    matrix: CounterfactualExperimentMatrix,
    fingerprint: ExperimentFingerprint,
    run_id: str,
    created_at: str,
) -> ExperimentLedgerRecord:
    if not isinstance(matrix, CounterfactualExperimentMatrix):
        raise TypeError("matrix must be CounterfactualExperimentMatrix")
    if not isinstance(fingerprint, ExperimentFingerprint):
        raise TypeError("fingerprint must be ExperimentFingerprint")
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("run_id must be non-empty")
    if not isinstance(created_at, str) or not created_at.strip():
        raise ValueError("created_at must be non-empty")

    payload = {
        "created_at": created_at,
        "fingerprint": fingerprint.as_dict(),
        "matrix": matrix.as_dict(),
        "run_id": run_id,
        "version": 2,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    identifier = sha256(canonical.encode("utf-8")).hexdigest()
    return ExperimentLedgerRecord(
        id=identifier,
        run_id=run_id,
        fingerprint=fingerprint,
        matrix=matrix,
        created_at=created_at,
    )


__all__ = ["ExperimentLedgerRecord", "create_experiment_ledger_record"]
