"""SQLite schema management for the MSG database."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Union


def connect(db_path: Union[str, Path]) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS msg_type (
            msg_id INTEGER PRIMARY KEY,
            uni_number INTEGER NOT NULL,
            litvin_number INTEGER NOT NULL,
            bns_number TEXT NOT NULL,
            og_number TEXT NOT NULL,
            number INTEGER NOT NULL,
            type INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS operation (
            operation_id INTEGER PRIMARY KEY,
            rotation_key TEXT NOT NULL,
            translation_key TEXT NOT NULL,
            time_reversal INTEGER NOT NULL CHECK (time_reversal IN (0, 1)),
            UNIQUE(rotation_key, translation_key, time_reversal)
        );

        CREATE TABLE IF NOT EXISTS msg_operation (
            msg_id INTEGER NOT NULL,
            operation_id INTEGER NOT NULL,
            operation_order INTEGER NOT NULL,
            PRIMARY KEY (msg_id, operation_id),
            FOREIGN KEY (msg_id) REFERENCES msg_type(msg_id) ON DELETE CASCADE,
            FOREIGN KEY (operation_id) REFERENCES operation(operation_id)
        );

        CREATE INDEX IF NOT EXISTS idx_msg_operation_operation_id
            ON msg_operation(operation_id);
        """
    )
    conn.commit()
