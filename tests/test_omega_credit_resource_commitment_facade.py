from src.omega_credit_allocation import create_omega_credit_allocation
from src.omega_credit_engine import OmegaCreditDistribution
from src.resource_state import create_resource_state
from thenet.engine import commit_omega_credit_resources


def test_runtime_facade_commits_omega_credit_allocation():
    distribution = OmegaCreditDistribution(
        id="distribution",
        total_credit=2.0,
        contributions=(("a", 1.0, 0.5), ("b", 1.0, 0.5)),
    )
    allocation = create_omega_credit_allocation(distribution, 40.0, 20.0)

    memory, compute = commit_omega_credit_resources(
        allocation,
        create_resource_state(50.0, 10.0, "t0"),
        create_resource_state(30.0, 5.0, "t0"),
        "t1",
    )

    assert memory.used == 50.0
    assert compute.used == 25.0
