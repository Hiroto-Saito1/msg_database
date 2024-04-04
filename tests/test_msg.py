# -*- coding: utf-8 -*-

from pathlib import Path
import sys
import os
import subprocess

tests_path = os.path.abspath(os.path.dirname(__file__))
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.append(src_path)


def test_msg_id():
    try:
        subprocess.run(
            "python {}".format(Path(src_path) / "get_msg_id.py"),
            shell=True,
            check=True,
        )
        assert True
    except:
        assert False
