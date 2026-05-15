"""package import の副作用を確認する単体テスト。"""

import importlib


def test_import_has_no_stdout(capsys):
    """import 時に CLI 処理や spglib 呼び出しが走らないことを確認する。"""

    importlib.import_module("msg_database")

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""
