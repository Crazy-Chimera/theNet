import asyncio

import pytest

from src.network import BootstrapNode, PeerClient


def test_bootstrap_two_agents_register_and_exchange_messages():
    async def scenario():
        bootstrap = BootstrapNode()
        port = await bootstrap.start()

        first = PeerClient("agent-a")
        second = PeerClient("agent-b")
        try:
            first_peers = await first.connect("127.0.0.1", port)
            assert first_peers == ()

            second_peers = await second.connect("127.0.0.1", port)
            assert [peer.peer_id for peer in second_peers] == ["agent-a"]
            assert [peer.peer_id for peer in bootstrap.peers] == ["agent-a", "agent-b"]

            await first.send("agent-b", {"proposal": "hello"})
            received = await second.receive()

            assert received == {
                "type": "message",
                "source": "agent-a",
                "target": "agent-b",
                "payload": {"proposal": "hello"},
            }
        finally:
            await first.close()
            await second.close()
            await bootstrap.stop()

    asyncio.run(scenario())


def test_unknown_target_is_reported():
    async def scenario():
        bootstrap = BootstrapNode()
        port = await bootstrap.start()
        client = PeerClient("agent-a")
        try:
            await client.connect("127.0.0.1", port)
            await client.send("missing", {"x": 1})
            assert await client.receive() == {
                "type": "error",
                "error": "target peer is not connected",
            }
        finally:
            await client.close()
            await bootstrap.stop()

    asyncio.run(scenario())


@pytest.mark.parametrize("peer_id", ["", "   ", None])
def test_peer_id_is_required(peer_id):
    with pytest.raises(ValueError):
        PeerClient(peer_id)


def test_message_requires_connection():
    async def scenario():
        client = PeerClient("agent-a")
        with pytest.raises(RuntimeError):
            await client.send("agent-b", {"x": 1})

    asyncio.run(scenario())
