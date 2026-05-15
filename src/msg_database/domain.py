"""MSG データを扱うための型付きドメインモデル。

このモジュールでは、spglib や SQLite の都合から独立した内部表現を定義する。
DB に保存する文字列キーは `OperationKey` のプロパティで必要なときだけ生成する。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any, Mapping, cast

MIN_MSG_ID = 1
MAX_MSG_ID = 1651


@dataclass(frozen=True, slots=True)
class MsgType:
    """spglib が返す MSG 種別情報を固定した値オブジェクト。"""

    msg_id: int
    uni_number: int
    litvin_number: int
    bns_number: str
    og_number: str
    number: int
    type: int

    @classmethod
    def from_mapping(cls, value: Mapping[str, object]) -> MsgType:
        """SQLite row や従来の dict から `MsgType` を復元する。"""

        return cls(
            msg_id=validate_msg_id(value["msg_id"]),
            uni_number=_as_int(value["uni_number"]),
            litvin_number=_as_int(value["litvin_number"]),
            bns_number=str(value["bns_number"]),
            og_number=str(value["og_number"]),
            number=_as_int(value["number"]),
            type=_as_int(value["type"]),
        )

    def as_dict(self) -> dict[str, object]:
        """CLI の JSON 出力に使いやすい dict へ変換する。"""

        return asdict(self)


@dataclass(frozen=True, slots=True)
class OperationKey:
    """磁気対称操作を安定比較するための内部キー。

    `rotation` と `translation` は内部では tuple と Fraction で保持する。
    文字列化は SQLite 保存または CLI 出力の境界でだけ行う。
    """

    rotation: tuple[int, ...]
    translation: tuple[Fraction, ...]
    time_reversal: bool

    def __post_init__(self) -> None:
        """内部表現の次元だけをここで検証する。"""

        if len(self.rotation) != 9:
            raise ValueError("rotation must contain 9 entries")
        if len(self.translation) != 3:
            raise ValueError("translation must contain 3 entries")

    @classmethod
    def from_storage(
        cls,
        rotation_key: str,
        translation_key: str,
        time_reversal: object,
    ) -> OperationKey:
        """SQLite/CLI の文字列キーから内部表現へ戻す。"""

        return cls(
            rotation=_parse_rotation_key(rotation_key),
            translation=_parse_translation_key(translation_key),
            time_reversal=bool(_as_int(time_reversal)),
        )

    @property
    def rotation_key(self) -> str:
        """SQLite に保存する行優先の rotation 文字列を返す。"""

        return ",".join(str(value) for value in self.rotation)

    @property
    def translation_key(self) -> str:
        """SQLite に保存する分数表記の translation 文字列を返す。"""

        return ",".join(_format_fraction(value) for value in self.translation)

    @property
    def time_reversal_int(self) -> int:
        """SQLite と JSON で扱いやすい 0/1 表現を返す。"""

        return int(self.time_reversal)

    def as_dict(self) -> dict[str, str | int]:
        """CLI の JSON 出力に使う保存表現へ変換する。"""

        return {
            "rotation_key": self.rotation_key,
            "translation_key": self.translation_key,
            "time_reversal": self.time_reversal_int,
        }


def validate_msg_id(msg_id: object) -> int:
    """spglib の MSG database が持つ ID 範囲に収まることを検証する。"""

    value = _as_int(msg_id)
    if not MIN_MSG_ID <= value <= MAX_MSG_ID:
        raise ValueError(f"msg_id must be between {MIN_MSG_ID} and {MAX_MSG_ID}")
    return value


def _as_int(value: object) -> int:
    """numpy scalar なども含めて int へ寄せる小さな変換関数。"""

    return int(cast(Any, value))


def _parse_rotation_key(value: str) -> tuple[int, ...]:
    """保存済み rotation_key を 9 要素の整数 tuple に戻す。"""

    rotation = tuple(int(part) for part in value.split(","))
    if len(rotation) != 9:
        raise ValueError("rotation key must contain 9 comma-separated integers")
    return rotation


def _parse_translation_key(value: str) -> tuple[Fraction, ...]:
    """保存済み translation_key を 3 要素の Fraction tuple に戻す。"""

    translation = tuple(Fraction(part) for part in value.split(","))
    if len(translation) != 3:
        raise ValueError("translation key must contain 3 comma-separated fractions")
    return translation


def _format_fraction(value: Fraction) -> str:
    """整数は整数表記、分数は numerator/denominator 表記にする。"""

    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"
