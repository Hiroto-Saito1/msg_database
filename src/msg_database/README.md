# src/msg_database

MSG DB の生成・検索ロジックを含む package です。

- `domain.py`: MSG 種別情報と operation key の型付きモデル。
- `normalize.py`: spglib の symmetry 出力を内部表現へ正規化。
- `builder.py`: provider から SQLite DB を生成するユースケース。
- `repository.py`: SQLite への保存・検索境界。
- `queries.py`: CLI や外部利用者向けの読み取り API。
- `cli.py`: コマンドライン引数と標準出力の制御。
- `db/`: SQLite 接続と schema。
- `providers/`: spglib など元データ取得元の adapter。
- `data/`: package に同梱する DB 成果物の置き場所。
