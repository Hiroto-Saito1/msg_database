"""spglibを用いて1651個のIDの対応を得るプログラム
"""

import numpy as np
from spglib import get_magnetic_spacegroup_type, get_magnetic_symmetry_from_database
import sqlite3


class GetMsgId:
    def __init__(self):
        # print(get_magnetic_symmetry_from_database(1))
        # self.make_example_database()
        pass

    def make_msg_type_table(self):
        msg_type = get_magnetic_spacegroup_type(1)
        conn = sqlite3.connect("msg_database.db")
        cur = conn.cursor()
        cur.execute(
            """CREATE TABLE msg_type (
                id INTEGER PRIMARY KEY,
                uni_number INTEGER,
                age INTEGER
        )"""
        )

        for i in range(1651):
            pass

    def make_example_database(self):
        """sqlite3でRDBの例を作成"""
        conn = sqlite3.connect("example.db")
        cur = conn.cursor()

        cur.execute(
            """CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                age INTEGER
        )"""
        )
        cur.execute(
            """CREATE TABLE jobs (
                name TEXT,
                job TEXT
        )"""
        )

        cur.execute("INSERT INTO users (name, age) VALUES ('Alice', 30)")
        cur.execute("INSERT INTO users (name, age) VALUES ('Bob', 25)")
        
        cur.execute("INSERT INTO jobs (name, job) VALUES ('Bob', 'doctor')")
        cur.execute("INSERT INTO jobs (name, job) VALUES ('Curry', 'teacher')")
        cur.execute("INSERT INTO jobs (name, job) VALUES ('Alice', 'engineer')")

        # name列が共通の場合の結合
        cur.execute('SELECT * FROM users JOIN jobs ON users.name = jobs.name')
        rows = cur.fetchall()
        for row in rows:
            print(row)
        # 変更の反映とクローズ
        conn.commit()
        conn.close()


if __name__ == "__main__":
    GetMsgId()
