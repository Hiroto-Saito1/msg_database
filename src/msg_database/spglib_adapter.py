"""旧 API 互換の spglib adapter。

新規コードでは `providers.spglib_provider.SpglibProvider` を使う。
"""

from __future__ import annotations

from typing import Any

from msg_database.providers.spglib_provider import SpglibProvider

_PROVIDER = SpglibProvider()


def get_msg_type(msg_id: int) -> dict[str, object]:
    """旧 API と同じ dict 形式で MSG 種別情報を返す。"""

    return _PROVIDER.get_msg_type(msg_id).as_dict()


def get_symmetry(msg_id: int) -> dict[str, Any]:
    """旧 API と同じ dict 形式で symmetry 情報を返す。"""

    return dict(_PROVIDER.get_symmetry(msg_id))
