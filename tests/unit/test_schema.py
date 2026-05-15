"""SQLite schema 作成の単体テスト。"""

from msg_database.schema import connect, create_schema


def test_create_schema_is_idempotent(tmp_path):
    """schema 作成は複数回実行しても壊れず、必要な table/index を作る。"""

    conn = connect(tmp_path / "msg.db")

    create_schema(conn)
    create_schema(conn)

    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }
    indexes = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'index'"
        ).fetchall()
    }

    assert {"metadata", "msg_type", "operation", "msg_operation"}.issubset(tables)
    assert "idx_msg_operation_operation_id" in indexes
    assert "idx_msg_operation_msg_id_order" in indexes
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
