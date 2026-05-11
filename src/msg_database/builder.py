"""Build a SQLite MSG database from spglib data."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Union

from msg_database.normalize import normalize_symmetry
from msg_database.repository import (
    MAX_MSG_ID,
    MIN_MSG_ID,
    MsgRepository,
    validate_msg_id,
)
from msg_database.schema import connect, create_schema
from msg_database.spglib_adapter import get_msg_type, get_symmetry


@dataclass(frozen=True)
class BuildStats:
    msg_type_count: int
    operation_count: int
    msg_operation_count: int


def build_database(
    db_path: Union[str, Path],
    msg_ids: Optional[Iterable[int]] = None,
) -> BuildStats:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()

    conn = connect(path)
    create_schema(conn)
    repo = MsgRepository(conn)

    for msg_id in _resolve_msg_ids(msg_ids):
        repo.upsert_msg_type(get_msg_type(msg_id))
        repo.set_msg_operations(msg_id, normalize_symmetry(get_symmetry(msg_id)))

    stats = BuildStats(
        msg_type_count=repo.count_msg_types(),
        operation_count=repo.count_operations(),
        msg_operation_count=repo.count_msg_operations(),
    )
    conn.close()
    return stats


def _resolve_msg_ids(msg_ids: Optional[Iterable[int]]) -> list[int]:
    if msg_ids is None:
        return list(range(MIN_MSG_ID, MAX_MSG_ID + 1))
    return [validate_msg_id(msg_id) for msg_id in msg_ids]
