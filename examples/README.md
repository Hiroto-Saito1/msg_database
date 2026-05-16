# 実行例

このディレクトリでは、どのような入力に対して、どのコマンドを実行し、どのような出力が得られるかをユースケースごとに示します。

例では、全 1651 件ではなく MSG ID `1` と `2` だけを含む小さな DB を作ります。出力が短く、動作確認にも使いやすいためです。

## 前提

開発環境では、先に editable install しておきます。

```bash
.venv/bin/python -m pip install -e ".[dev]"
```

以下の例では DB path として `/tmp/msg_examples.sqlite` を使います。別の場所に作りたい場合は、各コマンドの `--db` を変更してください。

## ユースケース 1: 少数の MSG ID だけで DB を作る

入力:

- 生成対象 MSG ID: `1`, `2`
- 出力先 DB: `/tmp/msg_examples.sqlite`

コマンド:

```bash
.venv/bin/msg-database build \
  --db /tmp/msg_examples.sqlite \
  --msg-id 1 \
  --msg-id 2
```

出力:

```json
{"msg_type_count": 2, "operation_count": 2, "msg_operation_count": 3}
```

意味:

- `msg_type_count`: 登録された MSG の数です。
- `operation_count`: 重複排除後の operation の数です。
- `msg_operation_count`: MSG と operation の対応関係の数です。

ここでは MSG `1` と `2` の 2 件を登録し、operation は重複排除後に 2 種類、対応関係は 3 件あります。

## ユースケース 2: MSG ID から operation 一覧を取得する

入力:

- MSG ID: `1`
- DB: `/tmp/msg_examples.sqlite`
- 出力形式: `json`

コマンド:

```bash
.venv/bin/msg-database msg 1 \
  --db /tmp/msg_examples.sqlite \
  --format json
```

出力:

```json
{"msg_type": {"msg_id": 1, "uni_number": 1, "litvin_number": 1, "bns_number": "1.1", "og_number": "1.1.1", "number": 1, "type": 1}, "operations": [{"rotation_key": "1,0,0,0,1,0,0,0,1", "translation_key": "0,0,0", "time_reversal": 0}]}
```

表形式で見たい場合:

```bash
.venv/bin/msg-database msg 1 --db /tmp/msg_examples.sqlite
```

出力:

```text
MSG 1: 1.1
1,0,0,0,1,0,0,0,1	0,0,0	0
```

出力の各列は、左から次の意味です。

```text
rotation_key    translation_key    time_reversal
```

## ユースケース 3: MSG ID `2` の operation を確認する

入力:

- MSG ID: `2`
- DB: `/tmp/msg_examples.sqlite`
- 出力形式: `table`

コマンド:

```bash
.venv/bin/msg-database msg 2 --db /tmp/msg_examples.sqlite
```

出力:

```text
MSG 2: 1.2
1,0,0,0,1,0,0,0,1	0,0,0	0
1,0,0,0,1,0,0,0,1	0,0,0	1
```

MSG ID `2` には、同じ rotation/translation で `time_reversal` だけが異なる 2 つの operation が含まれます。

## ユースケース 4: operation から MSG ID を逆引きする

入力:

- `rotation_key`: `1,0,0,0,1,0,0,0,1`
- `translation_key`: `0,0,0`
- `time_reversal`: `0`
- DB: `/tmp/msg_examples.sqlite`
- 出力形式: `json`

コマンド:

```bash
.venv/bin/msg-database operation \
  --rotation 1,0,0,0,1,0,0,0,1 \
  --translation 0,0,0 \
  --time-reversal 0 \
  --db /tmp/msg_examples.sqlite \
  --format json
```

出力:

```json
{"msg_ids": [1, 2]}
```

意味:

この operation は MSG ID `1` と `2` の両方に含まれています。内部では、`operation` table で一致する operation を探し、`msg_operation` 中間テーブルを JOIN して MSG ID を取得しています。

## ユースケース 5: 該当する MSG がない operation を検索する

入力:

- `rotation_key`: `-1,0,0,0,-1,0,0,0,-1`
- `translation_key`: `0,0,0`
- `time_reversal`: `1`
- DB: `/tmp/msg_examples.sqlite`

コマンド:

```bash
.venv/bin/msg-database operation \
  --rotation=-1,0,0,0,-1,0,0,0,-1 \
  --translation 0,0,0 \
  --time-reversal 1 \
  --db /tmp/msg_examples.sqlite \
  --format json
```

出力:

```json
{"msg_ids": []}
```

`--rotation` の値が `-1` から始まる場合は、上の例のように `--rotation=...` の形式で渡してください。スペース区切りで `--rotation -1,...` と書くと、シェルや `argparse` が `-1,...` を別の option と誤解することがあります。

## ユースケース 6: DB の生成条件を確認する

入力:

- DB: `/tmp/msg_examples.sqlite`
- 出力形式: `table`

コマンド:

```bash
.venv/bin/msg-database metadata --db /tmp/msg_examples.sqlite
```

出力例:

```text
generated_at	2026-05-16T00:37:32+00:00
msg_id_max	1651
msg_id_min	1
normalization_translation_denominator	24
numpy_version	2.4.4
python_version	3.13.12
schema_version	1
spglib_version	2.7.0
```

`generated_at`、`numpy_version`、`python_version`、`spglib_version` は実行環境によって変わります。

## ユースケース 7: 全 MSG ID の DB を作る

全 1651 件を生成する場合は、`--msg-id` を指定しません。

コマンド:

```bash
.venv/bin/msg-database build --db data/generated/msg_database.sqlite
```

出力例:

```json
{"msg_type_count": 1651, "operation_count": 1430, "msg_operation_count": 38307}
```

この DB を使えば、全 MSG ID を対象に `msg` と `operation` の検索ができます。
