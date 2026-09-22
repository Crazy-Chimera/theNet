"""Runtime entry-point smoke tests."""

from __future__ import annotations

import subprocess
import sys


def test_module_entry_point_is_runnable() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "thenet"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "theNet runtime: ready"
    assert result.stderr == ""
