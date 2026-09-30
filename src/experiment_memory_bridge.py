"""Bridge verified Experiment Ledger records into immutable Ω² Memory."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from src.experiment_ledger import ExperimentLedgerRecord
from src.memory import MemoryRecord, create_memory


@dataclass(frozen=True)
class ExperimentMemoryBridge:
    ledger_id: str
    memory: MemoryRecord
    verification_id: str
    version: int = 1

    def as_dict(self) -> dict:
        return asdict(self)


def bridge_verified_experiment_to_memory(
    *,
    ledger: ExperimentLedgerRecord,
    subject_id: str,
    verification_id: str,
    created_at: str,
) -> ExperimentMemoryBridge:
    if not isinstance(ledger, ExperimentLedgerRecord):
        raise TypeError("ledger must be ExperimentLedgerRecord")
    if not isinstance(verification_id, str) or not verification_id.strip():
        raise ValueError("verification_id must be non-empty")
    if ledger.fingerprint.result_fingerprint != ledger.id:
        raise ValueError("ledger fingerprint does not match ledger identity")

    memory = create_memory(
        subject_id=subject_id,
        source_id=ledger.id,
        kind="verified-experiment",
        created_at=created_at,
    )
    return ExperimentMemoryBridge(
        ledger_id=ledger.id,
        memory=memory,
        verification_id=verification_id,
    )


__all__ = ["ExperimentMemoryBridge", "bridge_verified_experiment_to_memory"]
