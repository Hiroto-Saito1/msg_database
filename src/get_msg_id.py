# -*- coding: utf-8 -*-

"""spglibを用いて1651個のIDの対応を得るSQLデータベースを構築するモジュール。

Example:
    * python get_msg_id.py

Todo:
    * get_magnetic_symmetry_from_database で得られる (rotations, translation, time_reversals) の組について、1651個の和集合を取る。
"""

import os
import numpy as np
from spglib import get_magnetic_spacegroup_type, get_magnetic_symmetry_from_database
import sqlite3


class GetMsgId:
    def __init__(self):
        print(get_magnetic_symmetry_from_database(np.random.randint(1, 1651)))
        # print(get_magnetic_spacegroup_type(np.random.randint(1, 1651)))
        # self.make_msg_type_table()

    def make_msg_type_table(self):
        """データベースに磁気空間群の表を追加する。"""
        if os.path.exists("msg_database.db"):
            os.remove("msg_database.db")
        conn = sqlite3.connect("msg_database.db")
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE msg_type (
                msg_id INTEGER PRIMARY KEY,
                uni_number INTEGER,
                litvin_number INTEGER,
                bns_number TEXT,
                og_number TEXT,
                number INTEGER,
                type INTEGER
            )
            """
        )

        for i in range(1651):
            msg_type = get_magnetic_spacegroup_type(int(i + 1))
            cur.execute(
                """
            INSERT INTO msg_type 
            (uni_number, litvin_number, bns_number, og_number, number, type) 
            VALUES 
            (?, ?, ?, ?, ?, ?)
            """,
                (
                    msg_type["uni_number"],
                    msg_type["litvin_number"],
                    msg_type["bns_number"],
                    msg_type["og_number"],
                    msg_type["number"],
                    msg_type["type"],
                ),
            )
        table_name = "msg_type"
        cur.execute(f"SELECT * FROM {table_name}")
        rows = cur.fetchmany(10)
        for row in rows:
            print(row)
        conn.close()

    def make_example_database(self):
        """sqlite3でRDBの例を作成。結合を行う。"""
        conn = sqlite3.connect("example.db")
        cur = conn.cursor()

        cur.execute(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                age INTEGER
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE jobs (
                name TEXT,
                job TEXT
            )
            """
        )

        cur.execute("INSERT INTO users (name, age) VALUES ('Alice', 30)")
        cur.execute("INSERT INTO users (name, age) VALUES ('Bob', 25)")

        cur.execute("INSERT INTO jobs (name, job) VALUES ('Bob', 'doctor')")
        cur.execute("INSERT INTO jobs (name, job) VALUES ('Curry', 'teacher')")
        cur.execute("INSERT INTO jobs (name, job) VALUES ('Alice', 'engineer')")

        # name列が共通の場合の結合
        cur.execute("SELECT * FROM users JOIN jobs ON users.name = jobs.name")
        rows = cur.fetchall()
        for row in rows:
            print(row)
        # 変更の反映とクローズ
        conn.commit()
        conn.close()


if __name__ == "__main__":
    GetMsgId()
