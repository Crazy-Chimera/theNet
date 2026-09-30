import asyncio

import pytest

from src.identity import IdentityVault
from src.network import BootstrapNode, PeerClient


def test_bootstrap_two_agents_register_and_exchange_messages():
    async def scenario():
        bootstrap = BootstrapNode()
        port = await bootstrap.start()

        vault = IdentityVault(":memory:")
        first_identity = vault.create("first")
        second_identity = vault.create("second")
        first = PeerClient(first_identity, vault, "first")
        second = PeerClient(second_identity, vault, "second")
        try:
            first_peers = await first.connect("127.0.0.1", port)
            assert first_peers == ()

            second_peers = await second.connect("127.0.0.1", port)
            assert [peer.peer_id for peer in second_peers] == [first_identity.did]
            assert [peer.peer_id for peer in bootstrap.peers] == sorted(
                [first_identity.did, second_identity.did]
            )

            await first.send(second_identity.did, {"proposal": "hello"})
            received = await second.receive()

            assert received == {
                "type": "message",
                "source": first_identity.did,
                "target": second_identity.did,
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
        vault = IdentityVault(":memory:")
        client = PeerClient(vault.create("password"), vault, "password")
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


def test_message_requires_connection():
    async def scenario():
        vault = IdentityVault(":memory:")
        client = PeerClient(vault.create("password"), vault, "password")
        with pytest.raises(RuntimeError):
            await client.send("missing", {"x": 1})

    asyncio.run(scenario())
