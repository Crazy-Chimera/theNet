# Φ → Ω-Credit Integration Contract

## Purpose

Provide a narrow integration boundary that derives structural coherence from a Φ structure and combines it with an already verified relational-utility signal and resource efficiency to create Ω-Credit.

## Rule

Input:
- RelationalUtility
- Φ PhiStructure
- resource efficiency in [0,1]
- non-empty creation timestamp

The adapter computes coherence using phi_coherence and delegates credit construction to the existing Ω-Credit constructor.

## Invariants

1. Utility verification remains authoritative; the adapter cannot override it.
2. Coherence is derived only from the supplied Φ structure.
3. Resource efficiency is validated by the Ω-Credit constructor.
4. Unverified utility produces zero credit.
5. Verified credit equals utility × resource efficiency × Φ coherence.
6. No input object is mutated.
7. No external service is required.
8. The adapter does not establish consensus or permission to commit.
