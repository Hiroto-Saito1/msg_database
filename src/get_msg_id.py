"""spglibを用いて1651個のIDの対応を得るプログラム
"""

import numpy as np
from spglib import get_magnetic_spacegroup_type, get_magnetic_symmetry_from_database
import sqlite3


class GetMsgId:
    def __init__(self):
        # print(get_magnetic_spacegroup_type(1))
        print(get_magnetic_symmetry_from_database(1))


if __name__ == "__main__":
    GetMsgId()
