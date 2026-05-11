import pytest

from msg_database.normalize import OperationKey
from msg_database.repository import MsgRepository
from msg_database.schema import connect, create_schema


def make_repository(db_path):
    conn = connect(db_path)
    create_schema(conn)
    return MsgRepository(conn)


def sample_msg_type(msg_id=1):
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
    repo = make_repository(tmp_path / "msg.db")

    repo.upsert_msg_type(sample_msg_type(1))
    repo.upsert_msg_type(sample_msg_type(1))

    assert repo.count_msg_types() == 1
    assert repo.get_msg_type(1)["bns_number"] == "1.1"


def test_msg_id_must_be_in_spglib_range(tmp_path):
    repo = make_repository(tmp_path / "msg.db")

    with pytest.raises(ValueError, match="msg_id"):
        repo.upsert_msg_type(sample_msg_type(0))

    with pytest.raises(ValueError, match="msg_id"):
        repo.upsert_msg_type(sample_msg_type(1652))


def test_operation_lookup_is_bidirectional_and_deduplicated(tmp_path):
    repo = make_repository(tmp_path / "msg.db")
    identity = OperationKey("1,0,0,0,1,0,0,0,1", "0,0,0", 0)
    time_reversed_identity = OperationKey("1,0,0,0,1,0,0,0,1", "0,0,0", 1)

    repo.upsert_msg_type(sample_msg_type(1))
    repo.upsert_msg_type(sample_msg_type(2))
    repo.set_msg_operations(1, [identity, time_reversed_identity])
    repo.set_msg_operations(2, [identity])

    assert repo.count_operations() == 2
    assert repo.find_msg_ids_by_operation(identity) == [1, 2]
    assert repo.find_msg_ids_by_operation(time_reversed_identity) == [1]
    assert repo.find_operations_by_msg_id(1) == [identity, time_reversed_identity]
