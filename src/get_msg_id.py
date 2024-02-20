"""spglibを用いて1651個のIDの対応を得るプログラム
"""

import numpy as np
from spglib import get_magnetic_spacegroup_type, get_magnetic_symmetry_from_database
import sqlite3


class GetMsgId:
    def __init__(self):
        # print(get_magnetic_spacegroup_type(1))
        # print(get_magnetic_symmetry_from_database(1))
        self.make_example_database()

    def make_example_database(self):
        """sqlite3でRDBの例を作成"""
        # データベースファイルを作成し、コネクションを取得
        conn = sqlite3.connect("example.db")
        # カーソルを取得
        cur = conn.cursor()
        # テーブルを作成
        cur.execute(
            """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER
        )"""
        )
        # データを挿入
        cur.execute("INSERT INTO users (name, age) VALUES ('Alice', 30)")
        cur.execute("INSERT INTO users (name, age) VALUES ('Bob', 25)")
        # データベースからデータを取得
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        # 変更の反映とクローズ
        conn.commit()
        conn.close()

        for row in rows:
            print(row)


if __name__ == "__main__":
    GetMsgId()
