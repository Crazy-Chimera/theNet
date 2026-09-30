# V1.7 — Experiment Reproducibility & Fingerprint

The matrix receives two deterministic fingerprints:

- **design_fingerprint**: baseline graph identity + normalized case definitions + runtime contract.
- **result_fingerprint**: design fingerprint + normalized observed impact vectors.

Case ordering is normalized by case ID, so reordering a matrix does not change its fingerprint.

The fingerprint is an integrity/reproducibility identifier, not a quality score and not evidence of causality. A matching fingerprint means the encoded experiment design and observed deterministic runtime output matched under the same runtime contract.
