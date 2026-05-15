"""MSG SQLite DB を生成するユースケース層。

provider から取得した spglib 由来のデータを正規化し、SQLite に保存する。
生成は一時 DB に対して行い、成功したときだけ指定パスへ置き換える。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Iterable

import numpy as np

from msg_database.db.connection import SCHEMA_VERSION, connect, create_schema
from msg_database.domain import MAX_MSG_ID, MIN_MSG_ID, validate_msg_id
from msg_database.normalize import normalize_symmetry
from msg_database.providers import MsgDataProvider, SpglibProvider
from msg_database.repository import MsgRepository


@dataclass(frozen=True)
class BuildStats:
    """DB 生成後に確認した主要テーブルの件数。"""

    msg_type_count: int
    operation_count: int
    msg_operation_count: int


def build_database(
    db_path: str | Path,
    msg_ids: Iterable[int] | None = None,
    provider: MsgDataProvider | None = None,
) -> BuildStats:
    """指定された MSG ID 群から SQLite DB を生成する。

    `msg_ids` が未指定なら spglib database の全 MSG ID を対象にする。
    テストでは fake provider を渡すことで spglib 依存を切り離せる。
    """

    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.tmp")
    if tmp_path.exists():
        tmp_path.unlink()

    try:
        stats = _write_database(tmp_path, _resolve_msg_ids(msg_ids), provider)
        tmp_path.replace(path)
        return stats
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink()
        raise


def _write_database(
    path: Path,
    msg_ids: list[int],
    provider: MsgDataProvider | None,
) -> BuildStats:
    """一時 DB ファイルへ実際の書き込みを行う。"""

    source = provider or SpglibProvider()
    conn = connect(path)
    try:
        create_schema(conn)
        repo = MsgRepository(conn)
        with conn:
            repo.set_metadata(_build_metadata(source))
            for msg_id in msg_ids:
                repo.upsert_msg_type(source.get_msg_type(msg_id))
                repo.set_msg_operations(
                    msg_id,
                    normalize_symmetry(source.get_symmetry(msg_id)),
                )
        return BuildStats(
            msg_type_count=repo.count_msg_types(),
            operation_count=repo.count_operations(),
            msg_operation_count=repo.count_msg_operations(),
        )
    finally:
        conn.close()


def _build_metadata(provider: MsgDataProvider) -> dict[str, str]:
    """DB の再現性確認に必要なバージョン情報を集める。"""

    metadata = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "python_version": sys.version.split()[0],
        "numpy_version": np.__version__,
        "msg_id_min": str(MIN_MSG_ID),
        "msg_id_max": str(MAX_MSG_ID),
        "normalization_translation_denominator": "24",
    }
    metadata.update(provider.metadata())
    return metadata


def _resolve_msg_ids(msg_ids: Iterable[int] | None) -> list[int]:
    """対象 MSG ID を確定し、範囲外 ID を早めに拒否する。"""

    if msg_ids is None:
        return list(range(MIN_MSG_ID, MAX_MSG_ID + 1))
    return [validate_msg_id(msg_id) for msg_id in msg_ids]
