"""Small adapter around spglib for easier testing and replacement."""

from __future__ import annotations

from typing import Any

import spglib

from msg_database.repository import validate_msg_id


def get_msg_type(msg_id: int) -> dict[str, object]:
    msg_id = validate_msg_id(msg_id)
    msg_type = spglib.get_magnetic_spacegroup_type(msg_id)
    if msg_type is None:
        raise ValueError(f"spglib returned no MSG type for msg_id {msg_id}")
    return {
        "msg_id": msg_id,
        "uni_number": msg_type.uni_number,
        "litvin_number": msg_type.litvin_number,
        "bns_number": msg_type.bns_number,
        "og_number": msg_type.og_number,
        "number": msg_type.number,
        "type": msg_type.type,
    }


def get_symmetry(msg_id: int) -> dict[str, Any]:
    msg_id = validate_msg_id(msg_id)
    symmetry = spglib.get_magnetic_symmetry_from_database(msg_id)
    if symmetry is None:
        raise ValueError(f"spglib returned no symmetry for msg_id {msg_id}")
    return symmetry
