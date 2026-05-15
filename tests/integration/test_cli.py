"""CLI を subprocess で確認する統合テスト。"""

import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def run_cli(args, cwd):
    """テスト対象 package を PYTHONPATH で指定して CLI を実行する。"""

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
    """CLI で subset DB を生成し、MSG 検索・逆引き・metadata を確認する。"""

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

    metadata = run_cli(
        ["metadata", "--db", str(db_path), "--format", "json"],
        REPO_ROOT,
    )
    assert metadata.returncode == 0, metadata.stderr
    assert json.loads(metadata.stdout)["schema_version"] == "1"


def test_cli_help_documents_argument_shapes_and_defaults():
    """CLI help に引数形式とデフォルト DB パスが表示される。"""

    build_help = run_cli(["build", "--help"], REPO_ROOT)
    assert build_help.returncode == 0
    assert "--msg-id MSG_ID" in build_help.stdout
    assert "integer in the range 1-1651" in build_help.stdout
    assert "data/generated/msg_database.sqlite" in build_help.stdout

    operation_help = run_cli(["operation", "--help"], REPO_ROOT)
    assert operation_help.returncode == 0
    assert "--rotation R11,R12,...,R33" in operation_help.stdout
    assert "--translation T1,T2,T3" in operation_help.stdout
    assert "--time-reversal {0,1}" in operation_help.stdout
    assert "9 comma-separated integer rotation entries" in operation_help.stdout


def test_cli_rejects_invalid_msg_id(tmp_path):
    """CLI build は範囲外 MSG ID を非ゼロ終了で拒否する。"""

    db_path = tmp_path / "msg.db"

    result = run_cli(["build", "--db", str(db_path), "--msg-id", "0"], REPO_ROOT)

    assert result.returncode != 0
    assert "msg_id" in result.stderr
