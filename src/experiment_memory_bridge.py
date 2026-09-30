"""Bridge independently reproduced experiment records into immutable Ω² Memory."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from src.counterfactual_reproducibility import compare_fingerprints
from src.experiment_ledger import (
    ExperimentLedgerRecord,
    compute_experiment_ledger_id,
)
from src.memory import MemoryRecord, create_memory


@dataclass(frozen=True)
class ExperimentMemoryBridge:
    baseline_record_id: str
    verification_record_id: str
    memory: MemoryRecord | None
    verified: bool
    reason: str
    version: int = 1

    def as_dict(self) -> dict:
        return asdict(self)


def _ledger_integrity_ok(record: ExperimentLedgerRecord) -> bool:
    try:
        expected = compute_experiment_ledger_id(
            run_id=record.run_id,
            fingerprint=record.fingerprint,
            matrix=record.matrix,
            created_at=record.created_at,
            version=record.version,
        )
    except (TypeError, ValueError):
        return False
    return expected == record.id


def bridge_verified_experiment_to_memory(
    *,
    baseline: ExperimentLedgerRecord,
    verification: ExperimentLedgerRecord,
    subject_id: str,
    created_at: str,
) -> ExperimentMemoryBridge:
    if not isinstance(baseline, ExperimentLedgerRecord):
        raise TypeError("baseline must be ExperimentLedgerRecord")
    if not isinstance(verification, ExperimentLedgerRecord):
        raise TypeError("verification must be ExperimentLedgerRecord")

    if baseline.id == verification.id:
        return ExperimentMemoryBridge(
            baseline.id, verification.id, None, False,
            "verification record must be distinct",
        )

    if not _ledger_integrity_ok(baseline):
        raise ValueError("baseline ledger identity does not match its content")
    if not _ledger_integrity_ok(verification):
        raise ValueError("verification ledger identity does not match its content")

    comparison = compare_fingerprints(
        baseline.fingerprint,
        verification.fingerprint,
    )
    verified = (
        comparison["same_design"]
        and comparison["same_result"]
        and comparison["same_baseline"]
        and comparison["same_runtime_contract"]
    )
    if not verified:
        return ExperimentMemoryBridge(
            baseline.id, verification.id, None, False,
            "independent ledger reproduction does not match",
        )

    memory = create_memory(
        subject_id=subject_id,
        source_id=baseline.id,
        kind="verified-experiment",
        created_at=created_at,
    )
    return ExperimentMemoryBridge(
        baseline.id, verification.id, memory, True,
        "independently reproduced experiment",
    )


__all__ = ["ExperimentMemoryBridge", "bridge_verified_experiment_to_memory"]
