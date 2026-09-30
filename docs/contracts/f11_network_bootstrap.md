# F11.5-F11.8 — Genesis → Network → Collective Bootstrap

F11.5 admits an Agent only after identity binding, Genesis anchoring and a valid Ed25519 challenge signature. Admission produces immutable NetworkMembership but does not itself grant consensus authority.

F11.6 establishes a signed two-party handshake over a deterministic transcript containing network, initiator, responder and nonce.

F11.7 introduces a common network Genesis anchor. One root Genesis can produce distinct Agent GenesisRecords while each record retains the common network_genesis_id. This resolves the distinction between individual Agent Genesis and the shared Network Genesis.

F11.8 creates three agents, admits all three, establishes two handshakes and executes the existing collective runtime with two verifier records and quorum 2. No parallel consensus mechanism is introduced.

Pipeline: Genesis → Identity → Admission → Handshake → Proposal → Verification → Consensus → Γ → Execution → Outcome → Ω-Credit → Resources → Commit → State.
