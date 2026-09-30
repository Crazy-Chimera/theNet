"""Runtime entry-point integration tests."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from urllib.request import urlopen


def test_module_entry_point_stays_alive_and_serves_health() -> None:
    env = os.environ.copy()
    env["PORT"] = "8766"

    process = subprocess.Popen(
        [sys.executable, "-m", "thenet"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        for _ in range(20):
            try:
                with urlopen("http://127.0.0.1:8766/health", timeout=1) as response:
                    assert response.status == 200
                    assert json.loads(response.read()) == {"status": "ready"}
                    break
            except Exception:
                time.sleep(0.25)
        else:
            raise AssertionError("runtime health endpoint did not become ready")

        assert process.poll() is None
    finally:
        process.terminate()
        process.wait(timeout=3)
