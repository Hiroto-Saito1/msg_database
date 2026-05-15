"""SQLite への保存と検索を担当する repository 層。

この層は `OperationKey` の内部表現と SQLite の保存表現の境界でもある。
呼び出し側のトランザクション制御を尊重するため、原則として commit は行わない。
"""

from __future__ import annotations

import sqlite3
from typing import Mapping

from msg_database.domain import MsgType, OperationKey, validate_msg_id


class MsgRepository:
    """MSG DB に対する低レベルな保存・検索 API。"""

    def __init__(self, conn: sqlite3.Connection):
        """既存の SQLite connection を受け取って repository を作る。"""

        self.conn = conn

    def upsert_msg_type(self, msg_type: MsgType | Mapping[str, object]) -> None:
        """MSG 種別情報を登録または更新する。"""

        record = (
            msg_type
            if isinstance(msg_type, MsgType)
            else MsgType.from_mapping(msg_type)
        )
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
                record.msg_id,
                record.uni_number,
                record.litvin_number,
                record.bns_number,
                record.og_number,
                record.number,
                record.type,
            ),
        )

    def get_msg_type(self, msg_id: int) -> MsgType:
        """指定 MSG ID の種別情報を取得する。"""

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
        return MsgType.from_mapping(dict(row))

    def count_msg_types(self) -> int:
        """`msg_type` テーブルの行数を返す。"""

        return int(self.conn.execute("SELECT COUNT(*) FROM msg_type").fetchone()[0])

    def count_operations(self) -> int:
        """重複排除後の operation 件数を返す。"""

        return int(self.conn.execute("SELECT COUNT(*) FROM operation").fetchone()[0])

    def count_msg_operations(self) -> int:
        """MSG と operation の対応件数を返す。"""

        return int(
            self.conn.execute("SELECT COUNT(*) FROM msg_operation").fetchone()[0]
        )

    def set_msg_operations(self, msg_id: int, operations: list[OperationKey]) -> None:
        """1 つの MSG に属する operation 一覧を順序付きで置き換える。"""

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

    def find_operations_by_msg_id(self, msg_id: int) -> list[OperationKey]:
        """MSG ID から対応する operation 一覧を順序付きで取得する。"""

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
            OperationKey.from_storage(
                str(row["rotation_key"]),
                str(row["translation_key"]),
                int(row["time_reversal"]),
            )
            for row in rows
        ]

    def find_msg_ids_by_operation(self, operation: OperationKey) -> list[int]:
        """中間テーブル `msg_operation` を JOIN して MSG ID を逆引きする。"""

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
                operation.time_reversal_int,
            ),
        ).fetchall()
        return [int(row["msg_id"]) for row in rows]

    def set_metadata(self, metadata: Mapping[str, str]) -> None:
        """生成時のメタデータを upsert する。"""

        for key, value in metadata.items():
            self.conn.execute(
                """
                INSERT INTO metadata (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value
                """,
                (key, value),
            )

    def get_metadata(self) -> dict[str, str]:
        """保存済みメタデータを key 昇順の dict として返す。"""

        rows = self.conn.execute(
            "SELECT key, value FROM metadata ORDER BY key"
        ).fetchall()
        return {str(row["key"]): str(row["value"]) for row in rows}

    def _upsert_operation(self, operation: OperationKey) -> int:
        """operation を重複排除して保存し、operation_id を返す。"""

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
                operation.time_reversal_int,
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
                operation.time_reversal_int,
            ),
        ).fetchone()
        if row is None:
            raise RuntimeError("failed to insert operation")
        return int(row["operation_id"])
