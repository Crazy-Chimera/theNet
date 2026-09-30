import asyncio

from src.agent import run_decision_cycle
from src.agent_state import create_agent_state
from src.genesis import create_genesis
from src.identity import IdentityVault
from src.memory_store import SQLiteMemoryStore, create_episodic_memory
from src.network import BootstrapNode, PeerClient
from src.omega_credit import create_omega_credit
from src.omega_credit_account import (
    create_omega_credit_account,
    earn_omega_credit,
    spend_omega_credit,
)
from src.proposal import create_proposal
from src.relation import create_relation
from src.timechain import (
    commit_branch,
    create_branch,
    create_timechain,
)


STAMP = "2026-09-30T00:00:00Z"


def test_identity_agent_memory_credit_network_timechain_flow(tmp_path):
    async def scenario():
        vault = IdentityVault(tmp_path / "vault.json")
        proposer_identity = vault.create("proposer")
        verifier_identity = vault.create("verifier")

        proposer = create_genesis(proposer_identity.did, STAMP)
        verifier = create_genesis(verifier_identity.did, STAMP)
        state = create_agent_state(proposer.id, "singularity:0", STAMP)
        proposal = create_proposal(
            proposer_identity.did,
            state.id,
            "verified collective proposal",
            STAMP,
        )
        relation = create_relation(proposer.id, verifier.id, "verifies", STAMP)

        cycle = run_decision_cycle(
            state,
            proposal,
            [relation],
            STAMP,
            identity=proposer_identity,
            vault=vault,
            password="proposer",
        )
        assert cycle.identity_verified is True

        memory = create_episodic_memory(
            proposer_identity.did,
            cycle.omega2.id,
            "proposal decision cycle completed",
            STAMP,
        )
        with SQLiteMemoryStore(tmp_path / "memory.sqlite") as store:
            store.save_episodic(memory)
            assert store.get_episodic(memory.id) == memory

        credit = create_omega_credit(
            proposer_identity.did,
            1.0,
            1.0,
            1.0,
            True,
            STAMP,
        )
        account = earn_omega_credit(
            create_omega_credit_account(proposer_identity.did),
            credit,
        )
        spent = spend_omega_credit(account, 0.25, "compute")
        assert spent.balance == 0.75

        chain = create_timechain(state.id)
        branch = create_branch(chain, "proposal")
        committed = commit_branch(branch, cycle.omega.to_state, proposal.id, STAMP)
        assert committed.current_state_id == proposal.id

        bootstrap = BootstrapNode()
        port = await bootstrap.start()
        proposer_client = PeerClient(proposer_identity, vault, "proposer")
        verifier_client = PeerClient(verifier_identity, vault, "verifier")
        try:
            await proposer_client.connect("127.0.0.1", port)
            await verifier_client.connect("127.0.0.1", port)
            await proposer_client.send(
                verifier_identity.did,
                {"proposal_id": proposal.id, "memory_id": memory.id},
            )
            message = await verifier_client.receive()
            assert message["payload"]["proposal_id"] == proposal.id
            assert message["payload"]["memory_id"] == memory.id
        finally:
            await proposer_client.close()
            await verifier_client.close()
            await bootstrap.stop()

    asyncio.run(scenario())
