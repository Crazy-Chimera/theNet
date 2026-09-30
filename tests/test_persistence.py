from thenet.persistence import PersistenceResult


def test_persistence_result_requires_exact_identity_match() -> None:
    result = PersistenceResult("g", "r", "g", "r")
    assert result.persisted is True


def test_persistence_result_rejects_identity_mismatch() -> None:
    result = PersistenceResult("g", "r", "other-g", "r")
    assert result.persisted is False
