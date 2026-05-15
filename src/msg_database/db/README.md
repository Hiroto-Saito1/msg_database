# src/msg_database/db

SQLite 接続と schema 定義を置くディレクトリです。

`schema.sql` が DB 構造の正本です。Python 側の `connection.py` は、外部キー制約を有効にした connection を作り、package data として同梱された schema を適用します。
