"""Deterministic network admission with signed challenges."""
from __future__ import annotations
from dataclasses import asdict,dataclass
from hashlib import sha256
import json
from src.agent_identity import AgentIdentity
from src.genesis_record import GenesisRecord
from src.identity import Identity,Signature,verify_signature
from src.network_identity import NetworkIdentity
from src.network_membership import NetworkMembership,create_network_membership

@dataclass(frozen=True)
class AdmissionRequest:
    request_id:str; network_id:str; agent_identity_id:str; challenge:str; signature:str; version:int=1
    def as_dict(self): return asdict(self)

@dataclass(frozen=True)
class AdmissionResult:
    request_id:str; admitted:bool; membership:NetworkMembership|None; reason:str; version:int=1
    def as_dict(self): return asdict(self)

def create_admission_challenge(network,agent,nonce):
    if not isinstance(network,NetworkIdentity) or not isinstance(agent,AgentIdentity): raise TypeError("invalid network or agent")
    if not isinstance(nonce,str) or not nonce.strip(): raise ValueError("nonce must be non-empty")
    payload={"agent_identity_id":agent.agent_identity_id,"genesis_id":agent.genesis_id,"network_id":network.network_id,"nonce":nonce,"version":1}
    return sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def create_admission_request(network,agent,identity,signature,nonce):
    if identity.did!=agent.identity_did: raise ValueError("signing identity does not match AgentIdentity")
    challenge=create_admission_challenge(network,agent,nonce)
    if not verify_signature(identity,challenge,signature): raise ValueError("admission signature is invalid")
    payload={"agent_identity_id":agent.agent_identity_id,"challenge":challenge,"network_id":network.network_id,"signature":signature.signature,"version":1}
    return AdmissionRequest(sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest(),network.network_id,agent.agent_identity_id,challenge,signature.signature)

def admit_agent(request,network,agent,genesis,identity,*,role="agent"):
    if not all(isinstance(v,t) for v,t in ((request,AdmissionRequest),(network,NetworkIdentity),(agent,AgentIdentity),(genesis,GenesisRecord),(identity,Identity))): raise TypeError("invalid admission inputs")
    if request.network_id!=network.network_id: return AdmissionResult(request.request_id,False,None,"network mismatch")
    if request.agent_identity_id!=agent.agent_identity_id: return AdmissionResult(request.request_id,False,None,"agent identity mismatch")
    if not verify_signature(identity,request.challenge,Signature(identity.did,request.signature)): return AdmissionResult(request.request_id,False,None,"invalid admission signature")
    if genesis.genesis_id!=agent.genesis_id: return AdmissionResult(request.request_id,False,None,"agent Genesis mismatch")
    anchor=genesis.network_genesis_id
    if not (network.genesis_id==genesis.genesis_id or (anchor is not None and network.genesis_id==anchor)): return AdmissionResult(request.request_id,False,None,"network Genesis anchor mismatch")
    membership=create_network_membership(network,agent,role=role,status="active")
    return AdmissionResult(request.request_id,True,membership,"admission verified")

__all__=["AdmissionRequest","AdmissionResult","admit_agent","create_admission_challenge","create_admission_request"]
