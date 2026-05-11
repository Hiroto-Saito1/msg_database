"""Normalize magnetic symmetry operations into stable SQLite keys."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any, Iterable, Mapping, Sequence, Union

import numpy as np


@dataclass(frozen=True)
class OperationKey:
    rotation_key: str
    translation_key: str
    time_reversal: int

    def as_dict(self) -> dict[str, Union[str, int]]:
        return asdict(self)


def normalize_operation(
    rotation: Sequence[Sequence[int]],
    translation: Sequence[Union[float, Fraction]],
    time_reversal: Union[bool, int],
) -> OperationKey:
    rotation_key = _normalize_rotation(rotation)
    translation_key = _normalize_translation(translation)
    return OperationKey(rotation_key, translation_key, int(bool(time_reversal)))


def normalize_symmetry(symmetry: Mapping[str, Any]) -> list[OperationKey]:
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


def _normalize_rotation(rotation: Sequence[Sequence[int]]) -> str:
    array = np.asarray(rotation, dtype=int)
    if array.shape != (3, 3):
        raise ValueError("rotation must be a 3x3 matrix")
    return ",".join(str(int(value)) for value in array.reshape(9))


def _normalize_translation(translation: Iterable[Union[float, Fraction]]) -> str:
    values = list(translation)
    if len(values) != 3:
        raise ValueError("translation must have 3 entries")
    return ",".join(_format_fraction(_to_fraction(value)) for value in values)


def _to_fraction(value: Union[float, Fraction]) -> Fraction:
    if isinstance(value, Fraction):
        return value.limit_denominator(24)

    if hasattr(value, "item"):
        value = value.item()

    return Fraction(str(float(value))).limit_denominator(24)


def _format_fraction(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"
