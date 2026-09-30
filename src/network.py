"""WebSocket bootstrap and peer relay boundary for theNet."""

from __future__ import annotations

from dataclasses import dataclass
import asyncio
import json
from typing import Any

from websockets.asyncio.client import connect
from websockets.asyncio.server import Server, ServerConnection, serve


@dataclass(frozen=True)
class Peer:
    peer_id: str
    host: str
    port: int


class BootstrapNode:
    """Minimal authenticated-by-registration peer registry and message relay."""

    def __init__(self) -> None:
        self._connections: dict[str, ServerConnection] = {}
        self._peers: dict[str, Peer] = {}
        self._lock = asyncio.Lock()
        self._server: Server | None = None

    @property
    def peers(self) -> tuple[Peer, ...]:
        return tuple(sorted(self._peers.values(), key=lambda peer: peer.peer_id))

    async def start(self, host: str = "127.0.0.1", port: int = 0) -> int:
        self._server = await serve(self._handle, host, port)
        socket = next(iter(self._server.sockets))
        return int(socket.getsockname()[1])

    async def stop(self) -> None:
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
        self._connections.clear()
        self._peers.clear()

    async def _handle(self, websocket: ServerConnection) -> None:
        peer_id: str | None = None
        try:
            async for raw in websocket:
                message = json.loads(raw)
                if not isinstance(message, dict):
                    raise ValueError("message must be an object")

                message_type = message.get("type")
                if message_type == "register":
                    peer_id = self._required_string(message, "peer_id")
                    remote = websocket.remote_address
                    host = str(remote[0]) if remote else "unknown"
                    port = int(remote[1]) if remote else 0

                    async with self._lock:
                        self._connections[peer_id] = websocket
                        self._peers[peer_id] = Peer(peer_id, host, port)
                        peers = [
                            {
                                "peer_id": peer.peer_id,
                                "host": peer.host,
                                "port": peer.port,
                            }
                            for peer in self.peers
                            if peer.peer_id != peer_id
                        ]

                    await websocket.send(
                        json.dumps(
                            {"type": "register_ack", "peer_id": peer_id, "peers": peers},
                            sort_keys=True,
                        )
                    )
                    continue

                if message_type == "message":
                    source = self._required_string(message, "source")
                    target = self._required_string(message, "target")
                    payload = message.get("payload")
                    if source not in self._connections or source != peer_id:
                        raise ValueError("message source is not registered connection")
                    target_socket = self._connections.get(target)
                    if target_socket is None:
                        await websocket.send(
                            json.dumps(
                                {"type": "error", "error": "target peer is not connected"},
                                sort_keys=True,
                            )
                        )
                        continue
                    await target_socket.send(
                        json.dumps(
                            {
                                "type": "message",
                                "source": source,
                                "target": target,
                                "payload": payload,
                            },
                            sort_keys=True,
                        )
                    )
                    continue

                raise ValueError("unsupported message type")
        finally:
            if peer_id is not None:
                async with self._lock:
                    if self._connections.get(peer_id) is websocket:
                        self._connections.pop(peer_id, None)
                        self._peers.pop(peer_id, None)

    @staticmethod
    def _required_string(message: dict[str, Any], name: str) -> str:
        value = message.get(name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be non-empty")
        return value


class PeerClient:
    """Small Agent-side WebSocket client used by local and integration runtimes."""

    def __init__(self, peer_id: str) -> None:
        if not isinstance(peer_id, str) or not peer_id.strip():
            raise ValueError("peer_id must be non-empty")
        self.peer_id = peer_id
        self._connection = None

    async def connect(self, host: str, port: int) -> tuple[Peer, ...]:
        self._connection = await connect(f"ws://{host}:{port}")
        await self._connection.send(
            json.dumps({"type": "register", "peer_id": self.peer_id}, sort_keys=True)
        )
        raw = await self._connection.recv()
        message = json.loads(raw)
        if message.get("type") != "register_ack":
            raise ValueError("bootstrap registration failed")
        return tuple(
            Peer(
                peer_id=item["peer_id"],
                host=item["host"],
                port=int(item["port"]),
            )
            for item in message.get("peers", [])
        )

    async def send(self, target: str, payload: Any) -> None:
        if self._connection is None:
            raise RuntimeError("peer is not connected")
        await self._connection.send(
            json.dumps(
                {
                    "type": "message",
                    "source": self.peer_id,
                    "target": target,
                    "payload": payload,
                },
                sort_keys=True,
            )
        )

    async def receive(self) -> dict[str, Any]:
        if self._connection is None:
            raise RuntimeError("peer is not connected")
        raw = await self._connection.recv()
        message = json.loads(raw)
        if not isinstance(message, dict):
            raise ValueError("received message must be an object")
        return message

    async def close(self) -> None:
        if self._connection is not None:
            await self._connection.close()
            self._connection = None


__all__ = ["BootstrapNode", "Peer", "PeerClient"]
