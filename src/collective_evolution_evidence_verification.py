"""Reference-level verification gate for collective evolution evidence."""

from __future__ import annotations

from collections.abc import Iterable

from src.collective_evolution_evidence import CollectiveEvolutionEvidence
from src.collective_evolution_evidence_integrity import (
    verify_collective_evolution_evidence_integrity,
)
from src.omega_credit_evolution_receipt_binding import (
    OmegaCreditEvolutionReceiptBinding,
)


def verify_collective_evolution_evidence(
    evidence: CollectiveEvolutionEvidence,
    bindings: Iterable[OmegaCreditEvolutionReceiptBinding],
) -> bool:
    """Verify that evidence references exactly the supplied binding objects."""
    if not verify_collective_evolution_evidence_integrity(evidence):
        return False

    items = tuple(bindings)

    if any(
        not isinstance(binding, OmegaCreditEvolutionReceiptBinding)
        for binding in items
    ):
        return False

    if len(items) != len({binding.id for binding in items}):
        return False

    by_id = {binding.id: binding for binding in items}

    if set(by_id) != set(evidence.binding_ids):
        return False

    for binding_id, commit_id, receipt_id, result_id in zip(
        evidence.binding_ids,
        evidence.commit_ids,
        evidence.receipt_ids,
        evidence.result_ids,
    ):
        binding = by_id[binding_id]
        if (
            binding.commit_id != commit_id
            or binding.receipt_id != receipt_id
            or binding.result_id != result_id
        ):
            return False

    return True


__all__ = ["verify_collective_evolution_evidence"]
