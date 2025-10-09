from __future__ import annotations

import subprocess
import sys


def test_gcp_json_crossfile_validation():
    result = subprocess.run(
        [sys.executable, "-m", "core.gcp_validate"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if result.returncode != 0:
        print(result.stdout)
    assert result.returncode == 0, "GCP JSON validation failed; see validator output."
