"""SQLite connection と schema 適用をまとめるモジュール。

schema 本体は `schema.sql` に置き、Python 側では接続設定と読み込みだけを扱う。
"""

from __future__ import annotations

import sqlite3
from importlib import resources
from pathlib import Path

SCHEMA_VERSION = "1"


def connect(db_path: str | Path) -> sqlite3.Connection:
    """row_factory と外部キー制約を有効にした SQLite connection を返す。"""

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    """同梱している `schema.sql` を使って必要な table/index を作る。"""

    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(_load_schema_sql())
    conn.commit()


def _load_schema_sql() -> str:
    """package data として同梱された schema.sql を読む。"""

    return resources.files("msg_database.db").joinpath("schema.sql").read_text()
