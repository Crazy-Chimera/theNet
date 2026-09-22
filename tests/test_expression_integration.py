from src.pi import create_meaning
from src.expression import create_expression


STAMP = "2026-09-22T00:10:00Z"


def test_pi_meaning_flows_into_psi_expression():
    meaning = create_meaning("convergence:1", "contribution:1", STAMP)
    expression = create_expression(meaning.id, "expression:1", STAMP)

    assert expression.meaning_id == meaning.id
    assert expression.expression_id == "expression:1"
    assert meaning.contribution_id == "contribution:1"
    assert expression.id != meaning.id
