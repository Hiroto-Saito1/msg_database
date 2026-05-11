import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_cli(args, cwd):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(cwd / "src")
    return subprocess.run(
        [sys.executable, "-m", "msg_database.cli", *args],
        cwd=cwd,
        env=env,
        check=False,
        text=True,
        capture_output=True,
    )


def test_cli_build_and_query_msg(tmp_path):
    db_path = tmp_path / "msg.db"

    build = run_cli(["build", "--db", str(db_path), "--msg-id", "1"], REPO_ROOT)
    assert build.returncode == 0, build.stderr

    query = run_cli(
        ["msg", "1", "--db", str(db_path), "--format", "json"],
        REPO_ROOT,
    )
    assert query.returncode == 0, query.stderr
    data = json.loads(query.stdout)

    assert data["msg_type"]["msg_id"] == 1
    assert data["msg_type"]["bns_number"] == "1.1"
    assert len(data["operations"]) == 1

    reverse = run_cli(
        [
            "operation",
            "--rotation",
            "1,0,0,0,1,0,0,0,1",
            "--translation",
            "0,0,0",
            "--time-reversal",
            "0",
            "--db",
            str(db_path),
            "--format",
            "json",
        ],
        REPO_ROOT,
    )
    assert reverse.returncode == 0, reverse.stderr
    assert json.loads(reverse.stdout)["msg_ids"] == [1]


def test_cli_rejects_invalid_msg_id(tmp_path):
    db_path = tmp_path / "msg.db"

    result = run_cli(["build", "--db", str(db_path), "--msg-id", "0"], REPO_ROOT)

    assert result.returncode != 0
    assert "msg_id" in result.stderr
