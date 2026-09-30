"""Ed25519 identity and encrypted local key vault for theNet MVP."""

from __future__ import annotations

from base64 import urlsafe_b64decode, urlsafe_b64encode
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import secrets

from cryptography.exceptions import InvalidSignature, InvalidTag
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


_VERSION = 1
_DID_METHOD = "thenet"
_AAD = b"theNet-identity-v1"
_SALT_BYTES = 16
_KEY_BYTES = 32


def _b64(value: bytes) -> str:
    return urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _unb64(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return urlsafe_b64decode((value + padding).encode("ascii"))


def _derive_key(password: str, salt: bytes) -> bytes:
    if not isinstance(password, str) or not password:
        raise ValueError("password must be non-empty")
    return Scrypt(
        salt=salt,
        length=_KEY_BYTES,
        n=2**14,
        r=8,
        p=1,
    ).derive(password.encode("utf-8"))


def _did(public_key: bytes) -> str:
    return f"did:{_DID_METHOD}:{sha256(public_key).hexdigest()}"


def verify_signature(identity: Identity, message: str | bytes, signature: Signature) -> bool:
    if not isinstance(identity, Identity) or not isinstance(signature, Signature):
        raise TypeError("identity and signature are required")
    payload = _message_bytes(message)
    if signature.did != identity.did:
        return False
    try:
        public_bytes = _unb64(identity.public_key)
        if identity.did != _did(public_bytes):
            return False
        public_key = Ed25519PublicKey.from_public_bytes(public_bytes)
        public_key.verify(_unb64(signature.signature), payload)
    except (InvalidSignature, ValueError):
        return False
    return True


def _message_bytes(message: str | bytes) -> bytes:
    if isinstance(message, str):
        return message.encode("utf-8")
    if isinstance(message, bytes):
        return message
    raise TypeError("message must be str or bytes")


@dataclass(frozen=True)
class Identity:
    did: str
    public_key: str
    version: int = _VERSION


@dataclass(frozen=True)
class Signature:
    did: str
    signature: str
    version: int = _VERSION


class IdentityVault:
    """Encrypted file-backed MVP vault for Ed25519 private keys.

    The vault protects private keys at rest with a password-derived AES-GCM key.
    Production deployments should replace this boundary with a managed KMS/HSM.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def _read(self) -> dict[str, dict[str, str]]:
        if not self.path.exists():
            return {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError("vault is unreadable") from exc
        if not isinstance(data, dict) or data.get("version") != _VERSION:
            raise ValueError("unsupported vault format")
        identities = data.get("identities", {})
        if not isinstance(identities, dict):
            raise ValueError("invalid vault identities")
        return identities

    def _write(self, identities: dict[str, dict[str, str]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(
            {"version": _VERSION, "identities": identities},
            sort_keys=True,
            separators=(",", ":"),
        )
        temporary = self.path.with_name(
            f".{self.path.name}.{secrets.token_hex(8)}.tmp"
        )
        try:
            temporary.write_text(payload, encoding="utf-8")
            try:
                temporary.chmod(0o600)
            except OSError:
                pass
            temporary.replace(self.path)
            try:
                self.path.chmod(0o600)
            except OSError:
                pass
        finally:
            if temporary.exists():
                temporary.unlink()

    def create(self, password: str) -> Identity:
        if not isinstance(password, str) or not password:
            raise ValueError("password must be non-empty")

        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        did = _did(public_key)

        identities = self._read()
        if did in identities:
            raise ValueError("identity already exists")

        salt = secrets.token_bytes(_SALT_BYTES)
        nonce = secrets.token_bytes(12)
        key = _derive_key(password, salt)
        encrypted = AESGCM(key).encrypt(
            nonce,
            private_key.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption(),
            ),
            _AAD,
        )
        identities[did] = {
            "public_key": _b64(public_key),
            "salt": _b64(salt),
            "nonce": _b64(nonce),
            "ciphertext": _b64(encrypted),
        }
        self._write(identities)
        return Identity(did=did, public_key=_b64(public_key))

    def get(self, did: str) -> Identity:
        identities = self._read()
        record = identities.get(did)
        if record is None:
            raise KeyError(did)
        return Identity(did=did, public_key=record["public_key"])

    def _private_key(self, did: str, password: str) -> Ed25519PrivateKey:
        identities = self._read()
        record = identities.get(did)
        if record is None:
            raise KeyError(did)
        try:
            key = _derive_key(password, _unb64(record["salt"]))
            raw = AESGCM(key).decrypt(
                _unb64(record["nonce"]),
                _unb64(record["ciphertext"]),
                _AAD,
            )
        except (ValueError, InvalidTag) as exc:
            raise ValueError("invalid vault password or corrupted key") from exc
        return Ed25519PrivateKey.from_private_bytes(raw)

    def sign(self, did: str, message: str | bytes, password: str) -> Signature:
        payload = _message_bytes(message)
        signature = self._private_key(did, password).sign(payload)
        return Signature(did=did, signature=_b64(signature))

    def verify(
        self,
        identity: Identity,
        message: str | bytes,
        signature: Signature,
    ) -> bool:
        return verify_signature(identity, message, signature)


__all__ = ["Identity", "IdentityVault", "Signature", "verify_signature"]
