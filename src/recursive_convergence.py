"""Multi-cycle recursive collective computation for Agent Ω.

This layer composes the v2.7 single-cycle runtime without changing its
consensus, credit, memory, or state-transition primitives.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from src.agent_state import AgentState
from src.collective_runtime import CollectiveComputationResult, run_collective_computation
from src.genesis_population import GenesisPopulation
from src.proposal import Proposal, create_proposal
from src.resource_state import ResourceState
from src.verification import create_verification
from src.recursive_learning_metrics import RecursiveLearningMetrics, measure_recursive_learning
from src.adaptive_resource_allocation import AdaptiveResourceAllocation, create_adaptive_resource_allocation


@dataclass(frozen=True)
class RecursiveCycle:
    index: int
    proposal: Proposal
    result: CollectiveComputationResult
    parent_memory_id: str | None
    parent_outcome_id: str | None


@dataclass(frozen=True)
class RecursiveConvergenceRun:
    cycles: tuple[RecursiveCycle, ...]
    initial_state: AgentState
    final_state: AgentState
    final_memory_resource: ResourceState
    final_compute_resource: ResourceState

    @property
    def cycle_count(self) -> int:
        return len(self.cycles)

    @property
    def all_converged(self) -> bool:
        return bool(self.cycles) and all(
            cycle.result.metrics.converged for cycle in self.cycles
        )

    @property
    def state_versions(self) -> tuple[int, ...]:
        return tuple(cycle.result.state.version for cycle in self.cycles)

    @property
    def memory_chain(self) -> tuple[str, ...]:
        return tuple(cycle.result.memory.id for cycle in self.cycles)

    @property
    def outcome_chain(self) -> tuple[str, ...]:
        return tuple(cycle.result.outcome.id for cycle in self.cycles)

    @property
    def learning_metrics(self) -> tuple[RecursiveLearningMetrics, ...]:
        return measure_recursive_learning(self.cycles)

    def adaptive_resource_allocation(
        self,
        memory_capacity: float,
        compute_capacity: float,
        *,
        improvement_bonus: float = 0.25,
    ) -> AdaptiveResourceAllocation:
        return create_adaptive_resource_allocation(
            self.learning_metrics,
            memory_capacity,
            compute_capacity,
            improvement_bonus=improvement_bonus,
        )


ProposalBuilder = Callable[
    [int, AgentState, RecursiveCycle | None],
    str,
]
Executor = Callable[[Proposal], str]
UtilityBuilder = Callable[[int, RecursiveCycle | None], float]


def run_recursive_convergence(
    *,
    population: GenesisPopulation,
    initial_state: AgentState,
    proposal_builder: ProposalBuilder,
    executor: Executor,
    quorum: int,
    new_singularity_builder: Callable[[int, Proposal], str],
    created_at: tuple[str, ...],
    memory_resource: ResourceState,
    compute_resource: ResourceState,
    utility: float = 1.0,
    utility_builder: UtilityBuilder | None = None,
) -> RecursiveConvergenceRun:
    """Run deterministic proposal→outcome→memory→next-proposal cycles.

    Each next proposal must target the state produced by the previous cycle.
    The previous cycle is exposed to the proposal builder explicitly through
    its immutable memory/outcome artifacts, making the recursive dependency
    observable rather than implicit.
    """
    if not isinstance(population, GenesisPopulation):
        raise TypeError("population must be GenesisPopulation")
    if not population.agents:
        raise ValueError("population must contain agents")
    if not isinstance(initial_state, AgentState):
        raise TypeError("initial_state must be AgentState")
    if not callable(proposal_builder):
        raise TypeError("proposal_builder must be callable")
    if not callable(executor):
        raise TypeError("executor must be callable")
    if not callable(new_singularity_builder):
        raise TypeError("new_singularity_builder must be callable")
    if utility_builder is not None and not callable(utility_builder):
        raise TypeError("utility_builder must be callable when provided")
    if not isinstance(created_at, tuple) or not created_at:
        raise ValueError("created_at must be a non-empty tuple")
    if len(created_at) < 1:
        raise ValueError("created_at must not be empty")

    verifiers = population.agents[1:]
    if quorum < 1 or quorum > len(verifiers):
        raise ValueError("quorum must be supported by independent verifiers")

    state = initial_state
    memory = memory_resource
    compute = compute_resource
    cycles: list[RecursiveCycle] = []
    prior_commits = []

    for index, timestamp in enumerate(created_at, start=1):
        previous = cycles[-1] if cycles else None
        proposal_text = proposal_builder(index, state, previous)
        if not isinstance(proposal_text, str) or not proposal_text.strip():
            raise ValueError("proposal_builder must return non-empty text")

        proposal = create_proposal(
            state.subject_id,
            state.id,
            proposal_text,
            timestamp,
        )
        verifications = tuple(
            # The proposer is always population.agents[0]; all remaining
            # agents are independent verifiers for this deterministic MVP.
            create_verification(
                proposal.id,
                verifier.subject_id,
                f"recursive-cycle:{index}:{verifier.subject_id}:{proposal.id}",
                True,
                timestamp,
            )
            for verifier in verifiers
        )
        result = run_collective_computation(
            current_state=state,
            proposal=proposal,
            verifications=verifications,
            quorum=quorum,
            new_singularity_id=new_singularity_builder(index, proposal),
            created_at=timestamp,
            memory_resource=memory,
            compute_resource=compute,
            executor=executor,
            utility=(
                utility_builder(index, previous)
                if utility_builder is not None
                else utility
            ),
            prior_commits=tuple(prior_commits),
        )
        cycles.append(
            RecursiveCycle(
                index=index,
                proposal=proposal,
                result=result,
                parent_memory_id=previous.result.memory.id if previous else None,
                parent_outcome_id=previous.result.outcome.id if previous else None,
            )
        )
        prior_commits.append(result.commit)
        state = result.state
        memory = result.memory_resource
        compute = result.compute_resource

    return RecursiveConvergenceRun(
        cycles=tuple(cycles),
        initial_state=initial_state,
        final_state=state,
        final_memory_resource=memory,
        final_compute_resource=compute,
    )


__all__ = ["RecursiveCycle", "RecursiveConvergenceRun", "run_recursive_convergence"]
