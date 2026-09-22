from thenet.engine import commit_self_organizing_resources
from src.relational_utility import create_relational_utility
from src.resource_state import create_resource_state


STAMP = "2026-09-22T12:00:00Z"


def _utility(contributor_id: str, verified: bool = True):
    return create_relational_utility(
        contributor_id=contributor_id,
        value=1.0,
        evidence_ids=(f"evidence-{contributor_id}",),
        verified=verified,
        created_at=STAMP,
    )


def test_engine_exposes_self_organizing_transition():
    memory = create_resource_state(10.0, 2.0, STAMP)
    compute = create_resource_state(20.0, 4.0, STAMP)

    next_memory, next_compute = commit_self_organizing_resources(
        [_utility("a"), _utility("b")],
        memory,
        compute,
        {"a": 1.0, "b": 1.0},
        "2026-09-22T12:01:00Z",
    )

    assert next_memory.used == 10.0
    assert next_compute.used == 20.0
    assert memory.used == 2.0
    assert compute.used == 4.0


def test_engine_self_organizing_transition_preserves_zero_credit():
    memory = create_resource_state(10.0, 2.0, STAMP)
    compute = create_resource_state(20.0, 4.0, STAMP)

    next_memory, next_compute = commit_self_organizing_resources(
        [_utility("a")],
        memory,
        compute,
        {"a": 0.0},
        "2026-09-22T12:01:00Z",
    )

    assert next_memory.used == memory.used
    assert next_compute.used == compute.used
