"""正規化ロジックの単体テスト。"""

from fractions import Fraction

import numpy as np

from msg_database.domain import OperationKey
from msg_database.normalize import normalize_operation, normalize_symmetry


def test_normalize_operation_uses_stable_keys():
    """float translation が安定した Fraction と保存キーへ変換される。"""

    operation = normalize_operation(
        np.eye(3, dtype=int),
        np.array([0.0, 0.5, 1.0 / 3.0]),
        False,
    )

    assert operation == OperationKey(
        rotation=(1, 0, 0, 0, 1, 0, 0, 0, 1),
        translation=(Fraction(0), Fraction(1, 2), Fraction(1, 3)),
        time_reversal=False,
    )
    assert operation.rotation_key == "1,0,0,0,1,0,0,0,1"
    assert operation.translation_key == "0,1/2,1/3"


def test_normalize_operation_accepts_fraction_and_boolish_time_reversal():
    """Fraction 入力と bool 系 time reversal を受け付ける。"""

    operation = normalize_operation(
        [[-1, 0, 0], [0, -1, 0], [0, 0, -1]],
        [Fraction(1, 2), Fraction(0), Fraction(3, 4)],
        True,
    )

    assert operation.rotation_key == "-1,0,0,0,-1,0,0,0,-1"
    assert operation.translation_key == "1/2,0,3/4"
    assert operation.time_reversal_int == 1


def test_normalize_symmetry_keeps_operation_order():
    """spglib symmetry dict の operation 順序を保持する。"""

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
        OperationKey.from_storage("1,0,0,0,1,0,0,0,1", "0,0,0", 0),
        OperationKey.from_storage("-1,0,0,0,-1,0,0,0,-1", "1/2,0,0", 1),
    ]
