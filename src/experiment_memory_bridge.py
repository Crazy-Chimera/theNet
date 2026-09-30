"""Bridge independently reproduced experiment records into immutable Ω² Memory."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from src.counterfactual_reproducibility import compare_fingerprints
from src.experiment_ledger import ExperimentLedgerRecord
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

    if baseline.fingerprint.result_fingerprint != baseline.id:
        raise ValueError("baseline fingerprint does not match ledger identity")
    if verification.fingerprint.result_fingerprint != verification.id:
        raise ValueError("verification fingerprint does not match ledger identity")

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
