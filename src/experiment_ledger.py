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


def compute_experiment_ledger_id(
    *,
    run_id: str,
    fingerprint: ExperimentFingerprint,
    matrix: CounterfactualExperimentMatrix,
    created_at: str,
    version: int = 2,
) -> str:
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("run_id must be non-empty")
    if not isinstance(fingerprint, ExperimentFingerprint):
        raise TypeError("fingerprint must be ExperimentFingerprint")
    if not isinstance(matrix, CounterfactualExperimentMatrix):
        raise TypeError("matrix must be CounterfactualExperimentMatrix")
    if not isinstance(created_at, str) or not created_at.strip():
        raise ValueError("created_at must be non-empty")
    if version != 2:
        raise ValueError("unsupported ledger version")

    payload = {
        "created_at": created_at,
        "fingerprint": fingerprint.as_dict(),
        "matrix": matrix.as_dict(),
        "run_id": run_id,
        "version": version,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(canonical.encode("utf-8")).hexdigest()


def create_experiment_ledger_record(
    *,
    matrix: CounterfactualExperimentMatrix,
    fingerprint: ExperimentFingerprint,
    run_id: str | None = None,
    created_at: str = "",
) -> ExperimentLedgerRecord:
    if not isinstance(matrix, CounterfactualExperimentMatrix):
        raise TypeError("matrix must be CounterfactualExperimentMatrix")
    if not isinstance(fingerprint, ExperimentFingerprint):
        raise TypeError("fingerprint must be ExperimentFingerprint")
    if run_id is None:
        run_id = created_at
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("run_id must be non-empty")
    if not isinstance(created_at, str) or not created_at.strip():
        raise ValueError("created_at must be non-empty")

    identifier = compute_experiment_ledger_id(
        run_id=run_id,
        fingerprint=fingerprint,
        matrix=matrix,
        created_at=created_at,
    )
    return ExperimentLedgerRecord(
        id=identifier,
        run_id=run_id,
        fingerprint=fingerprint,
        matrix=matrix,
        created_at=created_at,
    )


__all__ = [
    "ExperimentLedgerRecord",
    "compute_experiment_ledger_id",
    "create_experiment_ledger_record",
]
