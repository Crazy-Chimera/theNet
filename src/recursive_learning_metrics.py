"""Operational recursive-learning metrics for Agent Omega F10.1.

These metrics distinguish recursive repetition from measurable improvement.
They are deterministic project-level proxies, not a claim of intelligence.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.recursive_convergence import RecursiveCycle


_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+", re.UNICODE)


@dataclass(frozen=True)
class RecursiveLearningMetrics:
    cycle_index: int
    proposal_novelty: float
    utility: float
    omega_credit: float
    resource_efficiency: float
    k: float
    c: float
    r: int
    phi: float
    state_delta: int
    memory_dependency: bool
    verified_improvement: bool
    version: int = 1


def _tokens(text: str) -> set[str]:
    return {item.lower() for item in _TOKEN_RE.findall(text)}


def _novelty(current: str, previous: str | None) -> float:
    if previous is None:
        return 1.0
    left = _tokens(current)
    right = _tokens(previous)
    if not left and not right:
        return 0.0
    return 1.0 - (len(left & right) / max(len(left | right), 1))


def measure_recursive_learning(
    cycles: tuple["RecursiveCycle", ...],
) -> tuple[RecursiveLearningMetrics, ...]:
    """Measure each recursive cycle against its immediately preceding cycle.

    verified_improvement is true only when the proposal depends on prior
    memory and at least one measured performance dimension improves while no
    tracked dimension regresses. Dimensions are utility, Omega-Credit,
    resource efficiency, K, C, and Phi. R is structural and is reported but
    is not used as an improvement dimension.
    """
    metrics: list[RecursiveLearningMetrics] = []

    for index, cycle in enumerate(cycles):
        previous = cycles[index - 1] if index else None
        result = cycle.result

        if previous is None:
            improvement = False
        else:
            current = result
            prior = previous.result
            non_regression = (
                current.outcome.utility >= prior.outcome.utility
                                and current.metrics.k >= prior.metrics.k
                and current.metrics.c <= prior.metrics.c
                and current.metrics.phi >= prior.metrics.phi
            )
            strict_gain = (
                current.outcome.utility > prior.outcome.utility
                                or current.metrics.k > prior.metrics.k
                or current.metrics.c < prior.metrics.c
                or current.metrics.phi > prior.metrics.phi
            )
            improvement = (
                cycle.parent_memory_id == prior.memory.id
                and non_regression
                and strict_gain
            )

        previous_version = previous.result.state.version if previous else result.state.version - 1
        metrics.append(
            RecursiveLearningMetrics(
                cycle_index=cycle.index,
                proposal_novelty=_novelty(
                    cycle.proposal.proposal,
                    previous.proposal.proposal if previous else None,
                ),
                utility=result.outcome.utility,
                omega_credit=result.credit.credit,
                resource_efficiency=result.credit.resource_efficiency,
                k=result.metrics.k,
                c=result.metrics.c,
                r=result.metrics.r,
                phi=result.metrics.phi,
                state_delta=result.state.version - previous_version,
                memory_dependency=(
                    previous is not None
                    and cycle.parent_memory_id == previous.result.memory.id
                ),
                verified_improvement=improvement,
            )
        )

    return tuple(metrics)


__all__ = ["RecursiveLearningMetrics", "measure_recursive_learning"]
