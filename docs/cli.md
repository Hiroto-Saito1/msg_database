# CLI リファレンス

`msg-database` は `pyproject.toml` の console script として定義されています。

```toml
[project.scripts]
msg-database = "msg_database.cli:main"
```

実行される Python 関数は `src/msg_database/cli.py` の `main()` です。引数定義の正本は、同じファイルの `build_parser()` にあります。

## 共通事項

- DB パスの型はファイルシステム上のパスです。相対パスは、実行時のカレントディレクトリから解釈されます。
- 出力形式は `table` または `json` です。プログラムから処理する場合は `json` を使います。
- MSG ID は整数で、spglib の MSG database が持つ `1` から `1651` の範囲です。
- 実行時の詳細なヘルプは `msg-database <command> --help` で確認できます。

```bash
.venv/bin/msg-database --help
.venv/bin/msg-database build --help
.venv/bin/msg-database msg --help
.venv/bin/msg-database operation --help
.venv/bin/msg-database metadata --help
```

## `msg-database build`

spglib から MSG データを取得し、SQLite DB を生成します。

```bash
.venv/bin/msg-database build [--db PATH] [--msg-id MSG_ID ...]
```

| 引数 | 型/形式 | 必須 | デフォルト | 説明 |
|---|---|---:|---|---|
| `--db` | パス | いいえ | `data/generated/msg_database.sqlite` | 出力する SQLite DB のパス。親ディレクトリは自動作成されます。 |
| `--msg-id` | 整数、`1`-`1651` | いいえ | 全 MSG ID | 生成対象の MSG ID。複数回指定できます。省略時は `1` から `1651` まで全件を生成します。 |

例:

```bash
.venv/bin/msg-database build
.venv/bin/msg-database build --db /tmp/msg.db --msg-id 1 --msg-id 2
```

## `msg-database msg`

1 つの MSG ID から、MSG 種別情報と operation 一覧を取得します。

```bash
.venv/bin/msg-database msg MSG_ID [--db PATH] [--format {json,table}]
```

| 引数 | 型/形式 | 必須 | デフォルト | 説明 |
|---|---|---:|---|---|
| `MSG_ID` | 整数、`1`-`1651` | はい | なし | 検索する MSG ID。位置引数として渡します。 |
| `--db` | パス | いいえ | `data/generated/msg_database.sqlite` | 読み込む SQLite DB のパス。 |
| `--format` | `table` または `json` | いいえ | `table` | 出力形式。 |

例:

```bash
.venv/bin/msg-database msg 1
.venv/bin/msg-database msg 1 --db /tmp/msg.db --format json
```

## `msg-database operation`

正規化済み operation key から、その operation を含む MSG ID 一覧を逆引きします。

```bash
.venv/bin/msg-database operation \
  --rotation R11,R12,...,R33 \
  --translation T1,T2,T3 \
  --time-reversal {0,1} \
  [--db PATH] \
  [--format {json,table}]
```

| 引数 | 型/形式 | 必須 | デフォルト | 説明 |
|---|---|---:|---|---|
| `--rotation` | 9 個の整数をカンマ区切り | はい | なし | 3x3 rotation matrix を行優先で渡します。例: `1,0,0,0,1,0,0,0,1` |
| `--translation` | 3 個の整数または分数をカンマ区切り | はい | なし | translation vector を渡します。分数は `1/2` のように書けます。例: `0,1/2,0` |
| `--time-reversal` | `0` または `1` | はい | なし | 時間反転の有無。`0` は false、`1` は true です。 |
| `--db` | パス | いいえ | `data/generated/msg_database.sqlite` | 読み込む SQLite DB のパス。 |
| `--format` | `table` または `json` | いいえ | `table` | 出力形式。 |

例:

```bash
.venv/bin/msg-database operation \
  --rotation 1,0,0,0,1,0,0,0,1 \
  --translation 0,0,0 \
  --time-reversal 0 \
  --format json
```

## `msg-database metadata`

生成済み SQLite DB に保存された metadata を表示します。

```bash
.venv/bin/msg-database metadata [--db PATH] [--format {json,table}]
```

| 引数 | 型/形式 | 必須 | デフォルト | 説明 |
|---|---|---:|---|---|
| `--db` | パス | いいえ | `data/generated/msg_database.sqlite` | 読み込む SQLite DB のパス。 |
| `--format` | `table` または `json` | いいえ | `table` | 出力形式。 |

metadata には、`schema_version`、`generated_at`、`python_version`、`numpy_version`、`spglib_version` などが含まれます。
