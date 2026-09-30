"""F10.2 adaptive resource allocation from verified recursive improvement.

The allocator changes future resource shares only from immutable, measured
signals. A self-asserted improvement cannot increase allocation.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import math
from typing import Iterable

from src.recursive_learning_metrics import RecursiveLearningMetrics


@dataclass(frozen=True)
class AdaptiveResourceAllocation:
    id: str
    memory_by_cycle: tuple[tuple[int, float], ...]
    compute_by_cycle: tuple[tuple[int, float], ...]
    total_memory: float
    total_compute: float
    improvement_bonus: float
    version: int = 1


def _capacity(name: str, value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite non-negative number")
    value = float(value)
    if not math.isfinite(value) or value < 0.0:
        raise ValueError(f"{name} must be a finite non-negative number")
    return value


def _bonus(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("improvement_bonus must be a finite number in [0, 1]")
    value = float(value)
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError("improvement_bonus must be a finite number in [0, 1]")
    return value


def create_adaptive_resource_allocation(
    metrics: Iterable[RecursiveLearningMetrics],
    memory_capacity: float,
    compute_capacity: float,
    *,
    improvement_bonus: float = 0.25,
) -> AdaptiveResourceAllocation:
    """Allocate the next finite resource budget from verified performance.

    Base weight is verified Ω-Credit. Cycles marked verified_improvement receive
    a bounded multiplier. Non-improving cycles receive no multiplier. This is
    an allocation policy, not a claim that a cycle is intrinsically better.
    """
    items = tuple(metrics)
    if any(not isinstance(item, RecursiveLearningMetrics) for item in items):
        raise TypeError("metrics must contain only RecursiveLearningMetrics")

    memory = _capacity("memory_capacity", memory_capacity)
    compute = _capacity("compute_capacity", compute_capacity)
    bonus = _bonus(improvement_bonus)

    weights = tuple(
        (
            item.cycle_index,
            item.omega_credit * (1.0 + bonus if item.verified_improvement else 1.0),
        )
        for item in items
    )
    total_weight = math.fsum(weight for _index, weight in weights)

    if total_weight > 0.0:
        memory_by_cycle = tuple(
            (index, memory * weight / total_weight)
            for index, weight in weights
        )
        compute_by_cycle = tuple(
            (index, compute * weight / total_weight)
            for index, weight in weights
        )
    else:
        memory_by_cycle = tuple((index, 0.0) for index, _weight in weights)
        compute_by_cycle = tuple((index, 0.0) for index, _weight in weights)

    canonical = json.dumps(
        {
            "compute_by_cycle": compute_by_cycle,
            "improvement_bonus": bonus,
            "memory_by_cycle": memory_by_cycle,
            "total_compute": compute,
            "total_memory": memory,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    identifier = sha256(canonical.encode("utf-8")).hexdigest()

    return AdaptiveResourceAllocation(
        id=identifier,
        memory_by_cycle=memory_by_cycle,
        compute_by_cycle=compute_by_cycle,
        total_memory=memory,
        total_compute=compute,
        improvement_bonus=bonus,
    )


__all__ = [
    "AdaptiveResourceAllocation",
    "create_adaptive_resource_allocation",
]
