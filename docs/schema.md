# SQLite schema

この database は 4 つの table を使います。

- `metadata`: schema、Python、numpy、spglib など、DB の再現性確認に必要な metadata。
- `msg_type`: MSG ID ごとの種別情報。
- `operation`: 重複排除した磁気対称操作。
- `msg_operation`: MSG ID と operation の順序付き対応関係。

schema の正本は `src/msg_database/db/schema.sql` です。
