"""MSG 元データ provider の protocol 定義。

builder はこの protocol だけに依存するため、spglib 以外の fixture provider でも
同じ DB 生成処理をテストできる。
"""

from __future__ import annotations

from typing import Any, Mapping, Protocol

from msg_database.domain import MsgType


class MsgDataProvider(Protocol):
    def get_msg_type(self, msg_id: int) -> MsgType:
        """1 つの MSG ID に対応する種別情報を返す。"""

    def get_symmetry(self, msg_id: int) -> Mapping[str, Any]:
        """1 つの MSG ID に対応する生の symmetry dict を返す。"""

    def metadata(self) -> Mapping[str, str]:
        """生成 DB に保存する provider 固有の再現性メタデータを返す。"""
