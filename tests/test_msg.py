# -*- coding: utf-8 -*-

import subprocess
import sys
from pathlib import Path

SRC_PATH = Path(__file__).resolve().parents[1] / "src"


def test_legacy_script_shows_cli_help():
    result = subprocess.run(
        [sys.executable, str(SRC_PATH / "get_msg_id.py"), "--help"],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "msg_database" in result.stdout
