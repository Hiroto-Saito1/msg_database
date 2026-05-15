"""spglib を使って MSG 元データを取得する provider。"""

from __future__ import annotations

from typing import Any, Mapping

import spglib

from msg_database.domain import MsgType, validate_msg_id


class SpglibProvider:
    """spglib の magnetic space group database への薄い adapter。"""

    def get_msg_type(self, msg_id: int) -> MsgType:
        """spglib の MSG 種別情報を `MsgType` へ変換する。"""

        msg_id = validate_msg_id(msg_id)
        msg_type = spglib.get_magnetic_spacegroup_type(msg_id)
        if msg_type is None:
            raise ValueError(f"spglib returned no MSG type for msg_id {msg_id}")
        return MsgType(
            msg_id=msg_id,
            uni_number=msg_type.uni_number,
            litvin_number=msg_type.litvin_number,
            bns_number=msg_type.bns_number,
            og_number=msg_type.og_number,
            number=msg_type.number,
            type=msg_type.type,
        )

    def get_symmetry(self, msg_id: int) -> Mapping[str, Any]:
        """spglib の磁気対称操作 dict を取得する。"""

        msg_id = validate_msg_id(msg_id)
        symmetry = spglib.get_magnetic_symmetry_from_database(msg_id)
        if symmetry is None:
            raise ValueError(f"spglib returned no symmetry for msg_id {msg_id}")
        return symmetry

    def metadata(self) -> Mapping[str, str]:
        """生成 DB に保存する spglib バージョンを返す。"""

        return {"spglib_version": getattr(spglib, "__version__", "unknown")}
