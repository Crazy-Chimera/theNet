from src.omega_credit import create_omega_credit
from thenet.engine import aggregate_omega_credit


STAMP = "2026-09-22T00:00:00Z"


def test_runtime_facade_aggregates_omega_credit():
    first = create_omega_credit("agent-a", 0.7, 1.0, 1.0, True, STAMP)
    second = create_omega_credit("agent-b", 0.3, 1.0, 1.0, True, STAMP)

    distribution = aggregate_omega_credit([first, second])

    assert distribution.total_credit == 1.0
    assert distribution.contributions == (
        ("agent-a", 0.7, 0.7),
        ("agent-b", 0.3, 0.3),
    )
