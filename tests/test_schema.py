from msg_database.schema import connect, create_schema


def test_create_schema_is_idempotent(tmp_path):
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

    assert {"msg_type", "operation", "msg_operation"}.issubset(tables)
    assert "idx_msg_operation_operation_id" in indexes
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
