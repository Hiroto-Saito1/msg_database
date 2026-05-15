"""spglib の磁気対称操作を `OperationKey` へ正規化する。

浮動小数の丸め誤差を DB の一意キーへ直接入れないため、translation は
`Fraction(...).limit_denominator(24)` で安定した分数表現に変換する。
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from msg_database.domain import OperationKey


def normalize_operation(
    rotation: Sequence[Sequence[int]],
    translation: Sequence[float | Fraction],
    time_reversal: bool | int,
) -> OperationKey:
    """1 つの rotation/translation/time_reversal を内部キーへ変換する。"""

    return OperationKey(
        rotation=_normalize_rotation(rotation),
        translation=_normalize_translation(translation),
        time_reversal=bool(time_reversal),
    )


def normalize_symmetry(symmetry: Mapping[str, Any]) -> list[OperationKey]:
    """spglib の symmetry dict 全体を順序を保ったまま正規化する。"""

    rotations = symmetry["rotations"]
    translations = symmetry["translations"]
    time_reversals = symmetry["time_reversals"]

    if not (len(rotations) == len(translations) == len(time_reversals)):
        raise ValueError("rotations, translations, and time_reversals must align")

    return [
        normalize_operation(rotation, translation, time_reversal)
        for rotation, translation, time_reversal in zip(
            rotations, translations, time_reversals
        )
    ]


def _normalize_rotation(rotation: Sequence[Sequence[int]]) -> tuple[int, ...]:
    """3x3 rotation matrix を行優先の 9 要素 tuple にする。"""

    array = np.asarray(rotation, dtype=int)
    if array.shape != (3, 3):
        raise ValueError("rotation must be a 3x3 matrix")
    return tuple(int(value) for value in array.reshape(9))


def _normalize_translation(
    translation: Iterable[float | Fraction],
) -> tuple[Fraction, ...]:
    """3 要素 translation vector を Fraction tuple にする。"""

    values = list(translation)
    if len(values) != 3:
        raise ValueError("translation must have 3 entries")
    return tuple(_to_fraction(value) for value in values)


def _to_fraction(value: float | Fraction) -> Fraction:
    """float/numpy scalar/Fraction を denominator 24 以内の Fraction にする。"""

    if isinstance(value, Fraction):
        return value.limit_denominator(24)

    if hasattr(value, "item"):
        value = value.item()

    return Fraction(str(float(value))).limit_denominator(24)
