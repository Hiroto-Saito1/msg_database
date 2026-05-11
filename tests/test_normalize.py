from fractions import Fraction

import numpy as np

from msg_database.normalize import OperationKey, normalize_operation, normalize_symmetry


def test_normalize_operation_uses_stable_keys():
    operation = normalize_operation(
        np.eye(3, dtype=int),
        np.array([0.0, 0.5, 1.0 / 3.0]),
        False,
    )

    assert operation == OperationKey(
        rotation_key="1,0,0,0,1,0,0,0,1",
        translation_key="0,1/2,1/3",
        time_reversal=0,
    )


def test_normalize_operation_accepts_fraction_and_boolish_time_reversal():
    operation = normalize_operation(
        [[-1, 0, 0], [0, -1, 0], [0, 0, -1]],
        [Fraction(1, 2), Fraction(0), Fraction(3, 4)],
        True,
    )

    assert operation.rotation_key == "-1,0,0,0,-1,0,0,0,-1"
    assert operation.translation_key == "1/2,0,3/4"
    assert operation.time_reversal == 1


def test_normalize_symmetry_keeps_operation_order():
    symmetry = {
        "rotations": np.array(
            [
                np.eye(3, dtype=int),
                -np.eye(3, dtype=int),
            ]
        ),
        "translations": np.array(
            [
                [0.0, 0.0, 0.0],
                [0.5, 0.0, 0.0],
            ]
        ),
        "time_reversals": np.array([0, 1]),
    }

    operations = normalize_symmetry(symmetry)

    assert operations == [
        OperationKey("1,0,0,0,1,0,0,0,1", "0,0,0", 0),
        OperationKey("-1,0,0,0,-1,0,0,0,-1", "1/2,0,0", 1),
    ]
