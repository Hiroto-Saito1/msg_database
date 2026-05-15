# SQLite schema

The database uses four tables:

- `metadata`: reproducibility metadata such as schema, Python, numpy, and spglib versions.
- `msg_type`: one row per MSG ID.
- `operation`: deduplicated magnetic symmetry operations.
- `msg_operation`: ordered mapping between MSG IDs and operations.

The schema source lives in `src/msg_database/db/schema.sql`.
