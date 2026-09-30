"""CLI contract tests."""

from __future__ import annotations

import json
import subprocess
import sys


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "thenet", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_help_is_available() -> None:
    result = run_cli("--help")

    assert result.returncode == 0
    assert "genesis" in result.stdout
    assert "relation" in result.stdout
    assert "closure" in result.stdout
    assert "server" in result.stdout


def test_genesis_outputs_json() -> None:
    result = run_cli(
        "genesis",
        "--subject",
        "alpha",
        "--created-at",
        "2026-09-30T00:00:00Z",
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["subject"] == "alpha"
    assert payload["relations"] == []
    assert payload["version"] == 1
    assert len(payload["id"]) == 64


def test_relation_outputs_directed_json() -> None:
    result = run_cli(
        "relation",
        "--source-id",
        "alpha",
        "--target-id",
        "beta",
        "--kind",
        "supports",
        "--created-at",
        "2026-09-30T00:00:00Z",
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["source_id"] == "alpha"
    assert payload["target_id"] == "beta"
    assert payload["kind"] == "supports"
    assert len(payload["id"]) == 64


def test_commands_are_deterministic() -> None:
    args = (
        "genesis",
        "--subject",
        "alpha",
        "--created-at",
        "2026-09-30T00:00:00Z",
    )

    first = run_cli(*args)
    second = run_cli(*args)

    assert first.returncode == second.returncode == 0
    assert first.stdout == second.stdout


def test_closure_outputs_architecture_components() -> None:
    result = run_cli(
        "closure",
        "--source-subject",
        "alpha",
        "--target-subject",
        "beta",
        "--relation-kind",
        "supports",
        "--proposal-text",
        "test proposal",
        "--evidence",
        "test evidence",
        "--expression-id",
        "expr-1",
        "--created-at",
        "2026-09-30T00:00:00Z",
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)

    for key in (
        "source",
        "target",
        "relation",
        "phi",
        "omega",
        "omega2",
        "resonance",
        "proposal",
        "verification",
        "gamma",
        "pi",
        "psi",
        "theta",
        "rho",
        "sigma",
        "iota",
        "agent_state",
    ):
        assert key in payload


def test_invalid_genesis_returns_nonzero_and_no_stdout() -> None:
    result = run_cli(
        "genesis",
        "--subject",
        " ",
        "--created-at",
        "2026-09-30T00:00:00Z",
    )

    assert result.returncode == 2
    assert result.stdout == ""
    assert "subject must be non-empty" in result.stderr
