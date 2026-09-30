"""Signed Agent Ω network handshake."""
from __future__ import annotations
from dataclasses import asdict,dataclass
from hashlib import sha256
import json
from src.agent_identity import AgentIdentity
from src.identity import Identity,Signature,verify_signature
from src.network_identity import NetworkIdentity

@dataclass(frozen=True)
class Handshake:
    handshake_id:str; network_id:str; initiator_id:str; responder_id:str; transcript_hash:str; initiator_signature:str; responder_signature:str; version:int=1
    def as_dict(self): return asdict(self)

def create_handshake_transcript(network,initiator,responder,nonce):
    if not isinstance(network,NetworkIdentity) or not isinstance(initiator,AgentIdentity) or not isinstance(responder,AgentIdentity): raise TypeError("invalid handshake inputs")
    if initiator.agent_identity_id==responder.agent_identity_id: raise ValueError("handshake requires distinct agents")
    if not isinstance(nonce,str) or not nonce.strip(): raise ValueError("nonce must be non-empty")
    payload={"initiator_id":initiator.agent_identity_id,"network_id":network.network_id,"nonce":nonce,"responder_id":responder.agent_identity_id,"version":1}
    return sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def complete_handshake(network,initiator,responder,initiator_identity,responder_identity,initiator_signature,responder_signature,nonce):
    if initiator_identity.did!=initiator.identity_did or responder_identity.did!=responder.identity_did: raise ValueError("identity mismatch")
    transcript=create_handshake_transcript(network,initiator,responder,nonce)
    if not verify_signature(initiator_identity,transcript,initiator_signature): raise ValueError("initiator handshake signature is invalid")
    if not verify_signature(responder_identity,transcript,responder_signature): raise ValueError("responder handshake signature is invalid")
    payload={"initiator_id":initiator.agent_identity_id,"initiator_signature":initiator_signature.signature,"network_id":network.network_id,"responder_id":responder.agent_identity_id,"responder_signature":responder_signature.signature,"transcript_hash":transcript,"version":1}
    return Handshake(sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest(),network.network_id,initiator.agent_identity_id,responder.agent_identity_id,transcript,initiator_signature.signature,responder_signature.signature)

__all__=["Handshake","complete_handshake","create_handshake_transcript"]
