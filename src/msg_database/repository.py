"""Repository API for storing and querying MSG records."""

from __future__ import annotations

import sqlite3
from typing import Any, Mapping, cast

from msg_database.normalize import OperationKey

MIN_MSG_ID = 1
MAX_MSG_ID = 1651


class MsgRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def upsert_msg_type(self, msg_type: Mapping[str, object]) -> None:
        msg_id = validate_msg_id(msg_type["msg_id"])
        self.conn.execute(
            """
            INSERT INTO msg_type (
                msg_id,
                uni_number,
                litvin_number,
                bns_number,
                og_number,
                number,
                type
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(msg_id) DO UPDATE SET
                uni_number = excluded.uni_number,
                litvin_number = excluded.litvin_number,
                bns_number = excluded.bns_number,
                og_number = excluded.og_number,
                number = excluded.number,
                type = excluded.type
            """,
            (
                msg_id,
                _as_int(msg_type["uni_number"]),
                _as_int(msg_type["litvin_number"]),
                str(msg_type["bns_number"]),
                str(msg_type["og_number"]),
                _as_int(msg_type["number"]),
                _as_int(msg_type["type"]),
            ),
        )
        self.conn.commit()

    def get_msg_type(self, msg_id: int) -> dict[str, object]:
        row = self.conn.execute(
            """
            SELECT
                msg_id,
                uni_number,
                litvin_number,
                bns_number,
                og_number,
                number,
                type
            FROM msg_type
            WHERE msg_id = ?
            """,
            (validate_msg_id(msg_id),),
        ).fetchone()
        if row is None:
            raise KeyError(f"msg_id {msg_id} is not registered")
        return dict(row)

    def count_msg_types(self) -> int:
        return int(self.conn.execute("SELECT COUNT(*) FROM msg_type").fetchone()[0])

    def count_operations(self) -> int:
        return int(self.conn.execute("SELECT COUNT(*) FROM operation").fetchone()[0])

    def count_msg_operations(self) -> int:
        return int(
            self.conn.execute("SELECT COUNT(*) FROM msg_operation").fetchone()[0]
        )

    def set_msg_operations(self, msg_id: int, operations: list[OperationKey]) -> None:
        msg_id = validate_msg_id(msg_id)
        self.conn.execute("DELETE FROM msg_operation WHERE msg_id = ?", (msg_id,))
        for operation_order, operation in enumerate(operations):
            operation_id = self._upsert_operation(operation)
            self.conn.execute(
                """
                INSERT INTO msg_operation (msg_id, operation_id, operation_order)
                VALUES (?, ?, ?)
                ON CONFLICT(msg_id, operation_id) DO UPDATE SET
                    operation_order = excluded.operation_order
                """,
                (msg_id, operation_id, operation_order),
            )
        self.conn.commit()

    def find_operations_by_msg_id(self, msg_id: int) -> list[OperationKey]:
        rows = self.conn.execute(
            """
            SELECT
                operation.rotation_key,
                operation.translation_key,
                operation.time_reversal
            FROM msg_operation
            JOIN operation
                ON operation.operation_id = msg_operation.operation_id
            WHERE msg_operation.msg_id = ?
            ORDER BY msg_operation.operation_order, operation.operation_id
            """,
            (validate_msg_id(msg_id),),
        ).fetchall()
        return [
            OperationKey(
                str(row["rotation_key"]),
                str(row["translation_key"]),
                int(row["time_reversal"]),
            )
            for row in rows
        ]

    def find_msg_ids_by_operation(self, operation: OperationKey) -> list[int]:
        rows = self.conn.execute(
            """
            SELECT msg_operation.msg_id
            FROM operation
            JOIN msg_operation
                ON msg_operation.operation_id = operation.operation_id
            WHERE operation.rotation_key = ?
                AND operation.translation_key = ?
                AND operation.time_reversal = ?
            ORDER BY msg_operation.msg_id
            """,
            (
                operation.rotation_key,
                operation.translation_key,
                operation.time_reversal,
            ),
        ).fetchall()
        return [int(row["msg_id"]) for row in rows]

    def _upsert_operation(self, operation: OperationKey) -> int:
        self.conn.execute(
            """
            INSERT OR IGNORE INTO operation (
                rotation_key,
                translation_key,
                time_reversal
            )
            VALUES (?, ?, ?)
            """,
            (
                operation.rotation_key,
                operation.translation_key,
                operation.time_reversal,
            ),
        )
        row = self.conn.execute(
            """
            SELECT operation_id
            FROM operation
            WHERE rotation_key = ?
                AND translation_key = ?
                AND time_reversal = ?
            """,
            (
                operation.rotation_key,
                operation.translation_key,
                operation.time_reversal,
            ),
        ).fetchone()
        if row is None:
            raise RuntimeError("failed to insert operation")
        return int(row["operation_id"])


def validate_msg_id(msg_id: object) -> int:
    value = _as_int(msg_id)
    if not MIN_MSG_ID <= value <= MAX_MSG_ID:
        raise ValueError(f"msg_id must be between {MIN_MSG_ID} and {MAX_MSG_ID}")
    return value


def _as_int(value: object) -> int:
    return int(cast(Any, value))
