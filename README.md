# msg_database

`spglib` が提供する 1651 個の磁気空間群 MSG について、MSG 種別情報と磁気対称操作を SQLite に保存し、MSG ID と群操作の双方向検索を行うための小さな生成・検索ツールです。

## 方針

- Python 3.11 以上を対象にします。
- 依存関係は `pyproject.toml` を正本にします。
- SQLite DB は生成物として `data/generated/` に出力します。
- 内部ロジックでは型付きの `MsgType` と `OperationKey` を使い、DB 保存時だけ安定した文字列キーへ変換します。
- 生成時には `metadata` テーブルへ `spglib`、`numpy`、Python、schema version などを保存します。

## セットアップ

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[dev]"
```

## DB 生成

全 1651 件を生成します。

```bash
.venv/bin/msg-database build
```

出力先を指定する場合:

```bash
.venv/bin/msg-database build --db data/generated/msg_database.sqlite
```

少数の MSG ID だけで試す場合:

```bash
.venv/bin/msg-database build --db /tmp/msg.db --msg-id 1 --msg-id 2
```

## 検索

MSG ID から群操作一覧を JSON で取得します。

```bash
.venv/bin/msg-database msg 1 --db data/generated/msg_database.sqlite --format json
```

群操作から、それを含む MSG ID を逆引きします。

```bash
.venv/bin/msg-database operation \
  --rotation 1,0,0,0,1,0,0,0,1 \
  --translation 0,0,0 \
  --time-reversal 0 \
  --db data/generated/msg_database.sqlite \
  --format json
```

生成メタデータを確認します。

```bash
.venv/bin/msg-database metadata --db data/generated/msg_database.sqlite
```

## テスト

通常のテストでは slow テストを除外します。

```bash
.venv/bin/python -m pytest -q
```

全 1651 件の DB 構築を確認する場合:

```bash
.venv/bin/python -m pytest -q -m slow
```

品質確認:

```bash
.venv/bin/python -m ruff check .
.venv/bin/python -m mypy src
```

## 構成

```text
src/msg_database/
  domain.py                 # 型付きドメインモデル
  normalize.py              # spglib出力の正規化
  providers/spglib_provider.py
  db/connection.py
  db/schema.sql
  repository.py             # SQLite保存・検索
  builder.py                # DB生成ユースケース
  queries.py                # 読み取り用API
  cli.py
```
