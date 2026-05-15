"""生成済み MSG DB を読むための高レベル API。

CLI や外部利用者は repository を直接扱わず、このモジュール経由で取得する。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from msg_database.db.connection import connect
from msg_database.domain import MsgType, OperationKey, validate_msg_id
from msg_database.repository import MsgRepository


@dataclass(frozen=True, slots=True)
class MsgRecord:
    """MSG 種別情報と、その MSG に属する operation 一覧の組。"""

    msg_type: MsgType
    operations: list[OperationKey]

    def as_dict(self) -> dict[str, object]:
        """CLI の JSON 出力に使う dict へ変換する。"""

        return {
            "msg_type": self.msg_type.as_dict(),
            "operations": [operation.as_dict() for operation in self.operations],
        }


def get_msg_record(db_path: str | Path, msg_id: int) -> MsgRecord:
    """DB path と MSG ID から `MsgRecord` を取得する。"""

    conn = connect(db_path)
    try:
        repo = MsgRepository(conn)
        return MsgRecord(
            msg_type=repo.get_msg_type(validate_msg_id(msg_id)),
            operations=repo.find_operations_by_msg_id(msg_id),
        )
    finally:
        conn.close()


def find_msg_ids_by_operation(
    db_path: str | Path,
    operation: OperationKey,
) -> list[int]:
    """operation を含む MSG ID 一覧を取得する。"""

    conn = connect(db_path)
    try:
        return MsgRepository(conn).find_msg_ids_by_operation(operation)
    finally:
        conn.close()


def get_database_metadata(db_path: str | Path) -> dict[str, str]:
    """生成 DB に保存されている metadata を取得する。"""

    conn = connect(db_path)
    try:
        return MsgRepository(conn).get_metadata()
    finally:
        conn.close()
