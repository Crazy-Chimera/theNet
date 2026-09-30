"""Reproducibility fingerprints for Counterfactual Experiment Matrix V1.7."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json

from src.counterfactual_experiment_matrix import CounterfactualExperimentMatrix


FINGERPRINT_VERSION = 1
RUNTIME_CONTRACT = "counterfactual-matrix-v1.7"


@dataclass(frozen=True)
class ExperimentFingerprint:
    design_fingerprint: str
    result_fingerprint: str
    baseline_graph_id: str
    runtime_contract: str = RUNTIME_CONTRACT
    version: int = FINGERPRINT_VERSION

    def as_dict(self) -> dict:
        return asdict(self)


def _digest(payload: dict) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return sha256(canonical.encode("utf-8")).hexdigest()


def fingerprint_experiment_matrix(
    matrix: CounterfactualExperimentMatrix,
    baseline_graph_id: str,
) -> ExperimentFingerprint:
    if not isinstance(matrix, CounterfactualExperimentMatrix):
        raise TypeError("matrix must be CounterfactualExperimentMatrix")
    if not isinstance(baseline_graph_id, str) or not baseline_graph_id.strip():
        raise ValueError("baseline_graph_id must be non-empty")

    cases = [
        {
            "id": item.case.id,
            "cycle_index": item.case.cycle_index,
            "proposal_text": item.case.proposal_text,
            "version": item.case.version,
        }
        for item in matrix.cases
    ]
    design = _digest({
        "baseline_graph_id": baseline_graph_id,
        "baseline_cycles": matrix.baseline_cycles,
        "cases": sorted(cases, key=lambda item: item["id"]),
        "runtime_contract": RUNTIME_CONTRACT,
        "version": FINGERPRINT_VERSION,
    })

    results = [
        {
            "case": {
                "id": item.case.id,
                "cycle_index": item.case.cycle_index,
                "proposal_text": item.case.proposal_text,
                "version": item.case.version,
            },
            "impact_vector": item.impact_vector.as_dict(),
        }
        for item in matrix.cases
    ]
    result = _digest({
        "design_fingerprint": design,
        "results": sorted(results, key=lambda item: item["case"]["id"]),
        "runtime_contract": RUNTIME_CONTRACT,
        "version": FINGERPRINT_VERSION,
    })

    return ExperimentFingerprint(
        design_fingerprint=design,
        result_fingerprint=result,
        baseline_graph_id=baseline_graph_id,
    )


def compare_fingerprints(
    left: ExperimentFingerprint,
    right: ExperimentFingerprint,
) -> dict:
    if not isinstance(left, ExperimentFingerprint) or not isinstance(right, ExperimentFingerprint):
        raise TypeError("fingerprints must be ExperimentFingerprint")
    return {
        "same_design": left.design_fingerprint == right.design_fingerprint,
        "same_result": left.result_fingerprint == right.result_fingerprint,
        "same_baseline": left.baseline_graph_id == right.baseline_graph_id,
        "same_runtime_contract": left.runtime_contract == right.runtime_contract,
        "reproducible": (
            left.design_fingerprint == right.design_fingerprint
            and left.result_fingerprint == right.result_fingerprint
            and left.runtime_contract == right.runtime_contract
        ),
        "version": 1,
    }


__all__ = [
    "ExperimentFingerprint",
    "FINGERPRINT_VERSION",
    "RUNTIME_CONTRACT",
    "compare_fingerprints",
    "fingerprint_experiment_matrix",
]
