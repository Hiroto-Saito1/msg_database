# SQLite schema

この database は、MSG と群操作を検索しやすくするために SQLite で管理します。

SQL 初心者向けに言うと、この DB は「MSG の情報」「群操作そのもの」「MSG と群操作の対応関係」を別々の table に分けています。これは、同じ群操作が複数の MSG に出てくるためです。

schema の正本は `src/msg_database/db/schema.sql` です。

## table の役割

この database は 4 つの table を使います。

| table | 役割 |
|---|---|
| `metadata` | schema、Python、numpy、spglib など、DB の再現性確認に必要な metadata を保存します。 |
| `msg_type` | MSG ID ごとの種別情報を保存します。 |
| `operation` | 重複排除した磁気対称操作を保存します。 |
| `msg_operation` | MSG ID と operation を結ぶ中間テーブルです。 |

## なぜ中間テーブルが必要か

MSG と operation は **多対多** の関係です。

- 1 つの MSG は複数の operation を持ちます。
- 1 つの operation は複数の MSG に含まれます。

たとえば、単位操作のような operation は複数の MSG に現れます。このとき、各 MSG の行に operation をそのまま全部書き込むと、同じ operation が何度も保存されます。

そこで、この DB では次のように分けています。

```text
msg_type
  MSG そのものの情報

operation
  重複排除した operation の辞書

msg_operation
  どの MSG がどの operation を持つかを表す中間テーブル
```

関係を図で書くと、次のようになります。

```text
msg_type                      msg_operation                    operation
--------                      -------------                    ---------
msg_id = 1  ───────────────▶  msg_id = 1
                               operation_id = 10  ─────────▶  operation_id = 10
                                                              rotation_key = ...
                                                              translation_key = ...
                                                              time_reversal = ...

msg_id = 2  ───────────────▶  msg_id = 2
                               operation_id = 10  ─────────▶  同じ operation
```

`operation_id = 10` のような ID を共有することで、同じ operation を 1 回だけ保存し、複数の MSG から参照できます。

## `msg_type`

`msg_type` は MSG ごとの基本情報を保存します。

主な列:

| column | 意味 |
|---|---|
| `msg_id` | MSG ID。`1` から `1651`。primary key。 |
| `uni_number` | spglib が返す UNI number。 |
| `litvin_number` | Litvin number。 |
| `bns_number` | BNS 表記。 |
| `og_number` | OG 表記。 |
| `number` | 通常の space group number。 |
| `type` | MSG の type。 |

`msg_id` が primary key なので、同じ MSG ID は 1 行だけ保存されます。

## `operation`

`operation` は、重複排除した群操作を保存する辞書 table です。

主な列:

| column | 意味 |
|---|---|
| `operation_id` | operation の内部 ID。primary key。 |
| `rotation_key` | 3x3 rotation matrix を行優先で並べた文字列。例: `1,0,0,0,1,0,0,0,1` |
| `translation_key` | translation vector を分数表記で並べた文字列。例: `0,1/2,0` |
| `time_reversal` | 時間反転の有無。`0` または `1`。 |

この 3 つの値の組は一意です。

```sql
UNIQUE(rotation_key, translation_key, time_reversal)
```

そのため、同じ群操作が複数の MSG に現れても、`operation` table には 1 行だけ保存されます。

## `msg_operation`

`msg_operation` は、MSG と operation を結ぶ中間テーブルです。

主な列:

| column | 意味 |
|---|---|
| `msg_id` | `msg_type.msg_id` を参照します。 |
| `operation_id` | `operation.operation_id` を参照します。 |
| `operation_order` | その MSG 内での operation の順序です。 |

この table があることで、次の両方の検索ができます。

- MSG ID から、その MSG に含まれる operation 一覧を取得する。
- operation から、それを含む MSG ID 一覧を逆引きする。

## MSG ID から operation を検索する流れ

`msg-database msg 1` のように MSG ID から検索するときは、`msg_operation` を経由して `operation` を JOIN します。

```sql
SELECT
    operation.rotation_key,
    operation.translation_key,
    operation.time_reversal
FROM msg_operation
JOIN operation
    ON operation.operation_id = msg_operation.operation_id
WHERE msg_operation.msg_id = ?
ORDER BY msg_operation.operation_order, operation.operation_id;
```

流れは次の通りです。

```text
msg_id
  ↓
msg_operation で operation_id 一覧を探す
  ↓
operation table から operation の中身を取る
```

この処理は `src/msg_database/repository.py` の `find_operations_by_msg_id()` が担当します。

## operation から MSG ID を逆引きする流れ

`msg-database operation ...` のように群操作から逆引きするときは、まず `operation` table で一致する operation を探し、それを `msg_operation` と JOIN します。

```sql
SELECT msg_operation.msg_id
FROM operation
JOIN msg_operation
    ON msg_operation.operation_id = operation.operation_id
WHERE operation.rotation_key = ?
    AND operation.translation_key = ?
    AND operation.time_reversal = ?
ORDER BY msg_operation.msg_id;
```

流れは次の通りです。

```text
rotation_key / translation_key / time_reversal
  ↓
operation table で operation_id を探す
  ↓
msg_operation table で、その operation_id を持つ msg_id を探す
  ↓
MSG ID 一覧を返す
```

この処理は `src/msg_database/repository.py` の `find_msg_ids_by_operation()` が担当します。

## JOIN とは何か

`JOIN` は、複数の table を関連する列でつなげて読む SQL の機能です。

この DB では、`operation_id` がつなぎ目になります。

```sql
JOIN msg_operation
    ON msg_operation.operation_id = operation.operation_id
```

これは、「`operation` table の `operation_id` と、`msg_operation` table の `operation_id` が同じ行同士をつなげる」という意味です。

## この設計の利点

- 同じ operation を 1 回だけ保存できる。
- MSG から operation への検索と、operation から MSG への逆引きを同じ schema で実現できる。
- SQLite の `UNIQUE` 制約で operation の重複を防げる。
- `msg_operation.operation_order` により、spglib から得た operation の順序を保持できる。
