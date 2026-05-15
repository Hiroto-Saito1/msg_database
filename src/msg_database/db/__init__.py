"""SQLite support for msg_database."""

from msg_database.db.connection import SCHEMA_VERSION, connect, create_schema

__all__ = ["SCHEMA_VERSION", "connect", "create_schema"]
