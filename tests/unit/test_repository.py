"""SQLite repository の単体テスト。"""

import pytest

from msg_database.domain import OperationKey
from msg_database.repository import MsgRepository
from msg_database.schema import connect, create_schema


def make_repository(db_path):
    """一時 DB に schema を作成した repository を返す。"""

    conn = connect(db_path)
    create_schema(conn)
    return MsgRepository(conn)


def sample_msg_type(msg_id=1):
    """repository テスト用の最小 MSG 種別 dict を作る。"""

    return {
        "msg_id": msg_id,
        "uni_number": msg_id,
        "litvin_number": msg_id,
        "bns_number": f"{msg_id}.1",
        "og_number": f"{msg_id}.1.1",
        "number": msg_id,
        "type": 1,
    }


def test_upsert_and_get_msg_type(tmp_path):
    """MSG 種別情報は upsert され、重複登録されない。"""

    repo = make_repository(tmp_path / "msg.db")

    repo.upsert_msg_type(sample_msg_type(1))
    repo.upsert_msg_type(sample_msg_type(1))

    assert repo.count_msg_types() == 1
    assert repo.get_msg_type(1).bns_number == "1.1"


def test_msg_id_must_be_in_spglib_range(tmp_path):
    """MSG ID は spglib database の範囲外を拒否する。"""

    repo = make_repository(tmp_path / "msg.db")

    with pytest.raises(ValueError, match="msg_id"):
        repo.upsert_msg_type(sample_msg_type(0))

    with pytest.raises(ValueError, match="msg_id"):
        repo.upsert_msg_type(sample_msg_type(1652))


def test_operation_lookup_is_bidirectional_and_deduplicated(tmp_path):
    """operation は重複排除され、MSG からも operation からも検索できる。"""

    repo = make_repository(tmp_path / "msg.db")
    identity = OperationKey.from_storage("1,0,0,0,1,0,0,0,1", "0,0,0", 0)
    time_reversed_identity = OperationKey.from_storage(
        "1,0,0,0,1,0,0,0,1",
        "0,0,0",
        1,
    )

    repo.upsert_msg_type(sample_msg_type(1))
    repo.upsert_msg_type(sample_msg_type(2))
    repo.set_msg_operations(1, [identity, time_reversed_identity])
    repo.set_msg_operations(2, [identity])

    assert repo.count_operations() == 2
    assert repo.find_msg_ids_by_operation(identity) == [1, 2]
    assert repo.find_msg_ids_by_operation(time_reversed_identity) == [1]
    assert repo.find_operations_by_msg_id(1) == [identity, time_reversed_identity]


def test_metadata_is_upserted(tmp_path):
    """metadata table は同じ key を更新できる。"""

    repo = make_repository(tmp_path / "msg.db")

    repo.set_metadata({"schema_version": "1", "spglib_version": "old"})
    repo.set_metadata({"spglib_version": "new"})

    assert repo.get_metadata()["schema_version"] == "1"
    assert repo.get_metadata()["spglib_version"] == "new"
