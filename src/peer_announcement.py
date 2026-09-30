"""Signed peer announcements for F12 peer discovery."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from src.agent_identity import AgentIdentity
from src.identity import Identity, Signature, verify_signature
from src.network_identity import NetworkIdentity

@dataclass(frozen=True)
class PeerAnnouncement:
    announcement_id: str
    network_id: str
    agent_id: str
    identity_did: str
    epoch: int
    status: str
    signature: str
    version: int = 1

def _payload(network_id, agent_id, identity_did, epoch, status, version=1):
    return {"agent_id":agent_id,"epoch":epoch,"identity_did":identity_did,"network_id":network_id,"status":status,"version":version}

def create_peer_announcement(network: NetworkIdentity, agent: AgentIdentity, identity: Identity, epoch: int, status: str, signature: Signature) -> PeerAnnouncement:
    if identity.did != agent.identity_did: raise ValueError("identity does not match agent")
    payload = _payload(network.network_id,agent.agent_id,agent.identity_did,epoch,status)
    message = json.dumps(payload,sort_keys=True,separators=(",",":"))
    if not verify_signature(identity,message,signature): raise ValueError("peer announcement signature is invalid")
    announcement_id = sha256(json.dumps({**payload,"signature":signature.signature},sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return PeerAnnouncement(announcement_id,network.network_id,agent.agent_id,agent.identity_did,epoch,status,signature.signature)

def verify_peer_announcement(announcement: PeerAnnouncement, network: NetworkIdentity, agent: AgentIdentity, identity: Identity) -> bool:
    if announcement.network_id != network.network_id or announcement.agent_id != agent.agent_id or announcement.identity_did != agent.identity_did: return False
    payload = _payload(announcement.network_id,announcement.agent_id,announcement.identity_did,announcement.epoch,announcement.status,announcement.version)
    message = json.dumps(payload,sort_keys=True,separators=(",",":"))
    return verify_signature(identity,message,Signature(identity.did,announcement.signature,announcement.version))

__all__=["PeerAnnouncement","create_peer_announcement","verify_peer_announcement"]
