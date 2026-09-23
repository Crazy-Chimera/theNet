"""Pure integrity audit for collective evolution evidence."""

from __future__ import annotations

from src.collective_evolution_evidence import CollectiveEvolutionEvidence


def _valid_ids(values: tuple[str, ...]) -> bool:
    return all(isinstance(value, str) and bool(value.strip()) for value in values)


def verify_collective_evolution_evidence_integrity(
    evidence: CollectiveEvolutionEvidence,
) -> bool:
    """Validate the evidence reference surface without mutation or I/O."""
    if not isinstance(evidence, CollectiveEvolutionEvidence):
        return False

    if evidence.version != 1:
        return False

    if not isinstance(evidence.created_at, str) or not evidence.created_at.strip():
        return False

    binding_ids = evidence.binding_ids
    commit_ids = evidence.commit_ids
    receipt_ids = evidence.receipt_ids
    result_ids = evidence.result_ids

    if not all(
        isinstance(values, tuple)
        for values in (binding_ids, commit_ids, receipt_ids, result_ids)
    ):
        return False

    if not _valid_ids(binding_ids):
        return False
    if not _valid_ids(commit_ids):
        return False
    if not _valid_ids(receipt_ids):
        return False
    if not _valid_ids(result_ids):
        return False

    if len(binding_ids) != len(set(binding_ids)):
        return False

    cardinality = len(binding_ids)
    if any(
        len(values) != cardinality
        for values in (commit_ids, receipt_ids, result_ids)
    ):
        return False

    if not isinstance(evidence.id, str) or not evidence.id.strip():
        return False

    return True


__all__ = ["verify_collective_evolution_evidence_integrity"]
