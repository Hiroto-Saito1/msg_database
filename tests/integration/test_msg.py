# -*- coding: utf-8 -*-
"""互換用 legacy script の統合テスト。"""

import subprocess
import sys
from pathlib import Path

SRC_PATH = Path(__file__).resolve().parents[2] / "src"


def test_legacy_script_shows_cli_help():
    """古い `src/get_msg_id.py` 入口から CLI help を表示できる。"""

    result = subprocess.run(
        [sys.executable, str(SRC_PATH / "get_msg_id.py"), "--help"],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "msg_database" in result.stdout
