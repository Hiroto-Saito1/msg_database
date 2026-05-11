import spglib
import pytest

from msg_database.builder import build_database
from msg_database.repository import MsgRepository
from msg_database.schema import connect


@pytest.mark.integration
def test_build_database_for_selected_msg_ids(tmp_path):
    db_path = tmp_path / "msg.db"

    stats = build_database(db_path, msg_ids=[1, 2])
    repo = MsgRepository(connect(db_path))

    assert stats.msg_type_count == 2
    assert repo.count_msg_types() == 2
    assert repo.get_msg_type(1)["bns_number"] == "1.1"
    assert len(repo.find_operations_by_msg_id(1)) == len(
        spglib.get_magnetic_symmetry_from_database(1)["rotations"]
    )


@pytest.mark.slow
def test_build_database_for_all_msg_ids(tmp_path):
    db_path = tmp_path / "full.db"

    stats = build_database(db_path)
    repo = MsgRepository(connect(db_path))

    assert stats.msg_type_count == 1651
    assert repo.count_msg_types() == 1651
    assert repo.count_msg_operations() > 1651
    assert repo.find_operations_by_msg_id(1)
    assert repo.find_operations_by_msg_id(1651)
