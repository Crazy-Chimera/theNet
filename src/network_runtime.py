"""F12 live Network Runtime."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json as _json
import sqlite3
from pathlib import Path
from typing import Iterable
from src.agent_identity import AgentIdentity
from src.network_handshake import Handshake
from src.network_identity import NetworkIdentity
from src.network_membership import NetworkMembership

@dataclass(frozen=True)
class PeerDescriptor:
    agent_id: str
    identity_did: str
    role: str
    status: str
    network_id: str
    genesis_id: str
    version: int = 1

@dataclass(frozen=True)
class SessionState:
    session_id: str
    network_id: str
    initiator_id: str
    responder_id: str
    handshake_id: str
    state: str
    created_at: str
    version: int = 1

@dataclass(frozen=True)
class MembershipSnapshot:
    snapshot_id: str
    network_id: str
    epoch: int
    members: tuple[str, ...]
    quorum: int
    created_at: str
    version: int = 1

class NetworkRuntime:
    """Mutable live registry; snapshots are immutable computation boundaries."""
    def __init__(self, database: str | Path, network: NetworkIdentity, *, created_at: str = "") -> None:
        if not isinstance(network, NetworkIdentity): raise TypeError("network must be NetworkIdentity")
        self.database=str(database); self.network=network; self.created_at=created_at
        with self._connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS network_runtime_members (membership_id TEXT PRIMARY KEY, network_id TEXT NOT NULL, agent_id TEXT NOT NULL UNIQUE, genesis_id TEXT NOT NULL, role TEXT NOT NULL, status TEXT NOT NULL, identity_did TEXT NOT NULL, version INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS network_runtime_sessions (session_id TEXT PRIMARY KEY, network_id TEXT NOT NULL, initiator_id TEXT NOT NULL, responder_id TEXT NOT NULL, handshake_id TEXT NOT NULL UNIQUE, state TEXT NOT NULL, created_at TEXT NOT NULL, version INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS network_runtime_epochs (network_id TEXT PRIMARY KEY, epoch INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS network_runtime_snapshots (snapshot_id TEXT PRIMARY KEY, network_id TEXT NOT NULL, epoch INTEGER NOT NULL, members_json TEXT NOT NULL, quorum INTEGER NOT NULL, created_at TEXT NOT NULL, version INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS network_runtime_heartbeats (session_id TEXT PRIMARY KEY, network_id TEXT NOT NULL, seen_at TEXT NOT NULL, version INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS network_runtime_membership_events (event_id TEXT PRIMARY KEY, network_id TEXT NOT NULL, epoch INTEGER NOT NULL, agent_id TEXT NOT NULL, event_type TEXT NOT NULL, created_at TEXT NOT NULL, version INTEGER NOT NULL);
            """)
            db.execute("INSERT OR IGNORE INTO network_runtime_epochs VALUES (?,0)",(network.network_id,))

    def _connect(self):
        db=sqlite3.connect(self.database); db.row_factory=sqlite3.Row; return db
    def _bump_epoch(self,db):
        db.execute("UPDATE network_runtime_epochs SET epoch=epoch+1 WHERE network_id=?",(self.network.network_id,))
        return int(db.execute("SELECT epoch FROM network_runtime_epochs WHERE network_id=?",(self.network.network_id,)).fetchone()["epoch"])

    def _record_membership_event(self,db,agent_id,event_type,created_at):
        epoch=self._bump_epoch(db)
        event_id=_hash({"agent_id":agent_id,"created_at":created_at,"epoch":epoch,"event_type":event_type,"network_id":self.network.network_id,"version":1})
        db.execute("INSERT INTO network_runtime_membership_events VALUES (?,?,?,?,?,?,1)",(event_id,self.network.network_id,epoch,agent_id,event_type,created_at))
        return epoch

    def membership_events(self)->tuple[tuple[str,int,str,str,str],...]:
        with self._connect() as db:
            rows=db.execute("SELECT event_id,epoch,agent_id,event_type,created_at FROM network_runtime_membership_events WHERE network_id=? ORDER BY epoch,event_id",(self.network.network_id,)).fetchall()
        return tuple((r["event_id"],r["epoch"],r["agent_id"],r["event_type"],r["created_at"]) for r in rows)

    def add_agent(self,membership: NetworkMembership,agent: AgentIdentity)->PeerDescriptor:
        if not isinstance(membership,NetworkMembership) or not isinstance(agent,AgentIdentity): raise TypeError("invalid membership or agent")
        if membership.network_id!=self.network.network_id: raise ValueError("membership belongs to another network")
        if membership.agent_id!=agent.agent_id: raise ValueError("membership does not match agent")
        if membership.status!="active": raise ValueError("only active memberships can be added")
        with self._connect() as db:
            row=db.execute("SELECT * FROM network_runtime_members WHERE agent_id=?",(agent.agent_id,)).fetchone()
            if row:
                if row["membership_id"]!=membership.membership_id: raise ValueError("agent already has a different membership")
                if row["status"]!="active": db.execute("UPDATE network_runtime_members SET status='active' WHERE agent_id=?",(agent.agent_id,)); self._record_membership_event(db,agent.agent_id,"rejoin",self.created_at)
            else:
                db.execute("INSERT INTO network_runtime_members VALUES (?,?,?,?,?,?,?,?)",(membership.membership_id,membership.network_id,membership.agent_id,membership.genesis_id,membership.role,"active",agent.identity_did,membership.version)); self._record_membership_event(db,agent.agent_id,"join",self.created_at)
        return PeerDescriptor(agent.agent_id,agent.identity_did,membership.role,"active",membership.network_id,membership.genesis_id)

    def remove_agent(self,agent_id:str)->None:
        with self._connect() as db:
            row=db.execute("SELECT status FROM network_runtime_members WHERE agent_id=?",(agent_id,)).fetchone()
            if not row: raise KeyError(f"unknown agent: {agent_id}")
            if row["status"]=="active":
                db.execute("UPDATE network_runtime_members SET status='removed' WHERE agent_id=?",(agent_id,))
                db.execute("UPDATE network_runtime_sessions SET state='closed' WHERE initiator_id=? OR responder_id=?",(agent_id,agent_id)); self._record_membership_event(db,agent_id,"leave",self.created_at)

    def active_members(self)->tuple[PeerDescriptor,...]:
        with self._connect() as db: rows=db.execute("SELECT agent_id,identity_did,role,status,network_id,genesis_id FROM network_runtime_members WHERE network_id=? AND status='active' ORDER BY agent_id",(self.network.network_id,)).fetchall()
        return tuple(PeerDescriptor(r["agent_id"],r["identity_did"],r["role"],r["status"],r["network_id"],r["genesis_id"]) for r in rows)

    def discover_peers(self,agent_id:str)->tuple[PeerDescriptor,...]: return tuple(p for p in self.active_members() if p.agent_id!=agent_id)

    def register_handshake(self,handshake:Handshake,*,created_at:str)->SessionState:
        if handshake.network_id!=self.network.network_id: raise ValueError("handshake belongs to another network")
        active={p.agent_id for p in self.active_members()}
        if handshake.initiator_id not in active or handshake.responder_id not in active: raise ValueError("handshake endpoint is not an active member")
        sid=_hash({"created_at":created_at,"handshake_id":handshake.handshake_id,"network_id":self.network.network_id,"version":1})
        with self._connect() as db:
            try:
                db.execute("INSERT INTO network_runtime_sessions VALUES (?,?,?,?,?,?,?,1)",(sid,self.network.network_id,handshake.initiator_id,handshake.responder_id,handshake.handshake_id,"established",created_at))
            except sqlite3.IntegrityError as exc:
                raise ValueError("handshake replay or duplicate session") from exc
        return SessionState(sid,self.network.network_id,handshake.initiator_id,handshake.responder_id,handshake.handshake_id,"established",created_at)

    def heartbeat(self, session_id: str, *, seen_at: str) -> SessionState:
        with self._connect() as db:
            row=db.execute("SELECT * FROM network_runtime_sessions WHERE session_id=? AND network_id=?",(session_id,self.network.network_id)).fetchone()
            if row is None: raise KeyError(f"unknown session: {session_id}")
            if row["state"] != "established": raise ValueError("session is not established")
            db.execute("INSERT OR REPLACE INTO network_runtime_heartbeats VALUES (?,?,?,1)",(session_id,self.network.network_id,seen_at))
        return SessionState(row["session_id"],row["network_id"],row["initiator_id"],row["responder_id"],row["handshake_id"],row["state"],row["created_at"],row["version"])

    def last_heartbeat(self, session_id: str) -> str | None:
        with self._connect() as db:
            row=db.execute("SELECT seen_at FROM network_runtime_heartbeats WHERE session_id=? AND network_id=?",(session_id,self.network.network_id)).fetchone()
        return None if row is None else row["seen_at"]

    def sessions(self)->tuple[SessionState,...]:
        with self._connect() as db: rows=db.execute("SELECT * FROM network_runtime_sessions WHERE network_id=? ORDER BY session_id",(self.network.network_id,)).fetchall()
        return tuple(SessionState(r["session_id"],r["network_id"],r["initiator_id"],r["responder_id"],r["handshake_id"],r["state"],r["created_at"],r["version"]) for r in rows)

    def snapshot(self,*,created_at:str)->MembershipSnapshot:
        members=tuple(p.agent_id for p in self.active_members())
        with self._connect() as db:
            epoch=int(db.execute("SELECT epoch FROM network_runtime_epochs WHERE network_id=?",(self.network.network_id,)).fetchone()["epoch"])
            quorum=max(1,((len(members)-1)//2)+1)
            payload={"created_at":created_at,"epoch":epoch,"members":members,"network_id":self.network.network_id,"quorum":quorum,"version":1}; sid=_hash(payload)
            db.execute("INSERT INTO network_runtime_snapshots VALUES (?,?,?,?,?,?,1)",(sid,self.network.network_id,epoch,_json.dumps(members,separators=(",",":")),quorum,created_at))
        return MembershipSnapshot(sid,self.network.network_id,epoch,members,quorum,created_at)

    def get_snapshot(self,snapshot_id:str)->MembershipSnapshot:
        with self._connect() as db: r=db.execute("SELECT * FROM network_runtime_snapshots WHERE snapshot_id=? AND network_id=?",(snapshot_id,self.network.network_id)).fetchone()
        if not r: raise KeyError(f"unknown snapshot: {snapshot_id}")
        members=tuple(_json.loads(r["members_json"])); expected=_hash({"created_at":r["created_at"],"epoch":r["epoch"],"members":members,"network_id":r["network_id"],"quorum":r["quorum"],"version":r["version"]})
        if expected!=r["snapshot_id"]: raise ValueError("membership snapshot integrity check failed")
        return MembershipSnapshot(r["snapshot_id"],r["network_id"],r["epoch"],members,r["quorum"],r["created_at"],r["version"])

    def validate_snapshot_current(self, snapshot: MembershipSnapshot) -> None:
        if self.get_snapshot(snapshot.snapshot_id) != snapshot:
            raise ValueError("snapshot does not match persisted state")
        with self._connect() as db:
            row=db.execute("SELECT epoch FROM network_runtime_epochs WHERE network_id=?",(self.network.network_id,)).fetchone()
        if int(row["epoch"]) != snapshot.epoch:
            raise ValueError("snapshot is stale relative to live membership epoch")

    def validate_snapshot_verifiers(self,snapshot:MembershipSnapshot,proposer_id:str,verifier_ids:Iterable[str])->None:
        if snapshot.network_id!=self.network.network_id: raise ValueError("snapshot belongs to another network")
        if self.get_snapshot(snapshot.snapshot_id)!=snapshot: raise ValueError("snapshot does not match persisted state")
        if proposer_id not in snapshot.members: raise ValueError("proposer is not in membership snapshot")
        ids=tuple(verifier_ids)
        if len(ids)!=len(set(ids)): raise ValueError("verifier ids must be unique")
        if proposer_id in ids: raise ValueError("proposer cannot verify its own proposal")
        if any(v not in snapshot.members for v in ids): raise ValueError("verifier is not in membership snapshot")
        if len(ids)<snapshot.quorum: raise ValueError("snapshot quorum has not been reached")

def _hash(payload:dict)->str: return sha256(_json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
__all__=["MembershipSnapshot","NetworkRuntime","PeerDescriptor","SessionState"]