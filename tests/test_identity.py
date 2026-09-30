from dataclasses import FrozenInstanceError

import pytest

from src.identity import Identity, IdentityVault, Signature


def test_create_identity_is_ed25519_and_persistent(tmp_path):
    vault_path = tmp_path / "identity-vault.json"
    vault = IdentityVault(vault_path)

    identity = vault.create("correct horse battery staple")

    assert identity.did.startswith("did:thenet:")
    assert len(identity.public_key) > 40
    assert vault.get(identity.did) == identity

    reloaded = IdentityVault(vault_path)
    assert reloaded.get(identity.did) == identity


def test_sign_and_verify_message(tmp_path):
    vault = IdentityVault(tmp_path / "vault.json")
    identity = vault.create("password")

    signed = vault.sign(identity.did, "hello", "password")

    assert signed.did == identity.did
    assert vault.verify(identity, "hello", signed) is True


def test_tampering_fails_verification(tmp_path):
    vault = IdentityVault(tmp_path / "vault.json")
    identity = vault.create("password")
    signed = vault.sign(identity.did, "hello", "password")

    assert vault.verify(identity, "hello!", signed) is False


def test_wrong_identity_fails_verification(tmp_path):
    vault = IdentityVault(tmp_path / "vault.json")
    first = vault.create("first")
    second = vault.create("second")
    signed = vault.sign(first.did, "hello", "first")

    assert vault.verify(second, "hello", signed) is False


def test_empty_message_is_valid(tmp_path):
    vault = IdentityVault(tmp_path / "vault.json")
    identity = vault.create("password")
    signed = vault.sign(identity.did, b"", "password")

    assert vault.verify(identity, b"", signed) is True


def test_large_message_is_supported(tmp_path):
    vault = IdentityVault(tmp_path / "vault.json")
    identity = vault.create("password")
    message = b"x" * (1024 * 1024)
    signed = vault.sign(identity.did, message, "password")

    assert vault.verify(identity, message, signed) is True


def test_wrong_password_is_rejected(tmp_path):
    vault = IdentityVault(tmp_path / "vault.json")
    identity = vault.create("password")

    with pytest.raises(ValueError, match="password"):
        vault.sign(identity.did, "hello", "wrong")


def test_unknown_identity_is_rejected(tmp_path):
    vault = IdentityVault(tmp_path / "vault.json")

    with pytest.raises(KeyError):
        vault.get("did:thenet:missing")


def test_invalid_inputs_are_rejected(tmp_path):
    vault = IdentityVault(tmp_path / "vault.json")

    with pytest.raises(ValueError):
        vault.create("")

    with pytest.raises(TypeError):
        vault.sign("missing", 123, "password")

    with pytest.raises(TypeError):
        vault.verify(
            Identity("did:thenet:x", "public"),
            123,
            Signature("did:thenet:x", "signature"),
        )


def test_identity_and_signature_are_immutable(tmp_path):
    vault = IdentityVault(tmp_path / "vault.json")
    identity = vault.create("password")
    signed = vault.sign(identity.did, "hello", "password")

    with pytest.raises(FrozenInstanceError):
        identity.did = "other"

    with pytest.raises(FrozenInstanceError):
        signed.did = "other"


def test_private_key_is_not_stored_in_plaintext(tmp_path):
    vault_path = tmp_path / "vault.json"
    vault = IdentityVault(vault_path)
    identity = vault.create("password")

    raw = vault_path.read_text(encoding="utf-8")

    assert identity.did in raw
    assert "PRIVATE" not in raw
    assert len(raw) < 10000
