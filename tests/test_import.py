import importlib


def test_import_has_no_stdout(capsys):
    importlib.import_module("msg_database")

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""
