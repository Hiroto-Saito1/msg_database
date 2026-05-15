# TDD completion plan for msg_database

## 目的

このプロジェクトの目的は、spglib が持つ 1651 個の磁気空間群 MSG について、MSG 番号、MSG 種別情報、磁気対称操作を SQLite に保存し、以下を安定して検索できるようにすることである。

- MSG 番号から、その MSG に含まれる群操作一覧を取得する。
- 群操作から、その操作を含む MSG 番号一覧を取得する。
- MSG の基本情報、たとえば `uni_number`, `litvin_number`, `bns_number`, `og_number`, `number`, `type` を取得する。

現在の実装は `get_magnetic_symmetry_from_database()` の呼び出し確認と、未呼び出しの `msg_type` テーブル作成処理が中心である。TDD では、まず仕様をテストとして固定し、DB 構築、正規化、検索 API、CLI の順に完成させる。

## 基本方針

1. テスト対象を「spglib の正しさ」ではなく「spglib の出力をこのプロジェクトがどう保存・検索するか」に置く。
2. DB ファイルを直接テストで使い回さず、各テストは一時ディレクトリ内の SQLite DB に対して実行する。
3. ランダムな MSG ID は使わない。テストでは MSG ID を明示し、結果を決定的にする。
4. 最初は少数の MSG ID で高速な単体テストを作り、最後に 1651 件全体を扱う統合テストを追加する。
5. 群操作は Python オブジェクトのまま比較しない。DB に保存でき、等価判定が安定する正規化表現を定義してからテストする。
6. CLI は薄く保ち、主要処理は関数またはクラスメソッドとしてテスト可能にする。

## 推奨ツール

### 実行環境

- Python 3.11 以上。
- `venv` または `conda`。研究用途で spglib や numpy を扱うため、ローカルでは conda でもよい。
- 依存関係は `pyproject.toml` を正本にし、CI では `pip install -e ".[dev]"` で再現する。

### 必須ライブラリ

- `numpy`: spglib の配列出力を扱う。
- `spglib`: MSG 情報と磁気対称操作の取得元。
- `pytest`: TDD の中心。

### 開発用に追加したいライブラリ

- `pytest-cov`: テストカバレッジ確認。
- `ruff`: lint と簡易フォーマット。小規模プロジェクトなので `black` と `flake8` を分けるより運用が軽い。
- `mypy`: 型検査。最初は厳格にしすぎず、DB レコードや正規化済み操作の型を固める用途に使う。

開発用依存は `pyproject.toml` の `dev` optional dependency にまとめる。

## 目標アーキテクチャ

実装は以下のように分ける。

```text
src/
  msg_database/
    __init__.py
    domain.py              # 型付きドメインモデル
    providers/
      spglib_provider.py   # spglib 呼び出しを薄く包む
    db/
      connection.py        # SQLite 接続
      schema.sql           # CREATE TABLE と index
    normalize.py           # 群操作の正規化
    builder.py             # DB 構築処理
    repository.py          # 検索 API
    queries.py             # 読み取り用API
    cli.py                 # コマンドライン入口
```

現在の `src/get_msg_id.py` は、最終的には CLI または builder の薄い呼び出しへ移す。`__init__` でランダム出力する副作用はテストしづらいためなくす。

## DB 設計方針

最低限、以下のテーブルを想定する。

```sql
CREATE TABLE msg_type (
    msg_id INTEGER PRIMARY KEY,
    uni_number INTEGER NOT NULL,
    litvin_number INTEGER NOT NULL,
    bns_number TEXT NOT NULL,
    og_number TEXT NOT NULL,
    number INTEGER NOT NULL,
    type INTEGER NOT NULL
);

CREATE TABLE metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE operation (
    operation_id INTEGER PRIMARY KEY,
    rotation_key TEXT NOT NULL,
    translation_key TEXT NOT NULL,
    time_reversal INTEGER NOT NULL,
    UNIQUE(rotation_key, translation_key, time_reversal)
);

CREATE TABLE msg_operation (
    msg_id INTEGER NOT NULL,
    operation_id INTEGER NOT NULL,
    operation_order INTEGER NOT NULL,
    PRIMARY KEY (msg_id, operation_id),
    FOREIGN KEY (msg_id) REFERENCES msg_type(msg_id),
    FOREIGN KEY (operation_id) REFERENCES operation(operation_id)
);

CREATE INDEX idx_msg_operation_operation_id ON msg_operation(operation_id);
```

`operation` は全 MSG に現れる群操作の重複を取り除いた辞書テーブルとする。`msg_operation` が MSG と operation の中間テーブルになる。

## 群操作の正規化方針

spglib の `get_magnetic_symmetry_from_database(msg_id)` は、概ね以下を返す。

- `rotations`: 整数の 3x3 行列列
- `translations`: 3 次元の実数ベクトル列
- `time_reversals`: bool または 0/1 の列

DB で一意性を保つため、保存前に次の形式へ変換する。

- `rotation_key`: 3x3 整数行列を行優先で `1,0,0,0,1,0,0,0,1` のような文字列にする。
- `translation`: 分数値として安定比較する。まずは `fractions.Fraction(x).limit_denominator(24)` を使う。
- `time_reversal`: `bool` にする。

DB 保存時だけ以下へ変換する。

- `rotation_key`: `1,0,0,0,1,0,0,0,1`
- `translation_key`: `0,1/2,0`
- `time_reversal`: `0` または `1`

浮動小数の丸め誤差を DB のキーに直接入れないことが重要である。

## TDD の進め方

### 1. 現在の副作用をなくすテスト

最初に「import しても標準出力が出ない」「ランダムな spglib 呼び出しが走らない」ことをテストする。

期待するテスト:

- `import msg_database` が副作用なしで成功する。
- CLI 実行時だけ処理が走る。

この段階で `GetMsgId.__init__()` のランダム出力を廃止する。

### 2. スキーマ作成の単体テスト

一時 DB に対して `create_schema(conn)` を実行し、テーブルと index が存在することを確認する。

期待するテスト:

- `msg_type`, `operation`, `msg_operation` が作成される。
- `create_schema(conn)` を複数回呼んでも壊れない。
- 外部キー制約が有効になる。

### 3. MSG 種別テーブルのテスト

spglib を直接使うテストは少数 ID に限定する。たとえば `msg_id=1`, `msg_id=2`, `msg_id=1651` を使う。

期待するテスト:

- 指定した MSG ID だけ `msg_type` に登録できる。
- `msg_id` は 1 から 1651 の範囲外を拒否する。
- 同じ MSG ID を二重登録しても重複しない、または明示的に更新される。

### 4. 群操作正規化の単体テスト

ここは spglib から切り離し、手書きの numpy 配列でテストする。

期待するテスト:

- 単位行列が期待する `rotation_key` になる。
- `0.5` と `Fraction(1, 2)` 相当の値が同じ `translation_key` になる。
- `True`, `False`, `1`, `0` が `time_reversal` の `1`, `0` に揃う。
- 同じ操作は同じキーになる。

### 5. operation と msg_operation 登録のテスト

少数の手書き操作を使って、重複排除と中間テーブル登録を確認する。

期待するテスト:

- 同一 operation は `operation` に 1 行だけ保存される。
- 複数 MSG が同一 operation を共有できる。
- `find_msg_ids_by_operation()` で該当 MSG ID が昇順に返る。
- `find_operations_by_msg_id()` で該当操作一覧が返る。

### 6. spglib 連携の統合テスト

ここで初めて spglib の実データを使う。

期待するテスト:

- 1 つの MSG ID について、spglib が返す操作数と DB に紐づく操作数が一致する。
- 複数 MSG ID を登録したとき、operation の重複排除が機能する。
- `msg_id=1` と `msg_id=1651` の登録が成功する。

### 7. 1651 件全体の統合テスト

通常の単体テストからは分け、遅いテストとして扱う。

期待するテスト:

- 1651 件すべての `msg_type` が作成される。
- `msg_operation` に全 MSG の操作が登録される。
- 全 MSG で `find_operations_by_msg_id(msg_id)` が空にならない。
- DB を再生成しても件数が再現する。

pytest marker を使い、普段は除外できるようにする。

```bash
pytest -m "not slow"
pytest -m slow
```

### 8. CLI のテスト

CLI は subprocess で最低限確認する。

期待するコマンド:

```bash
python -m msg_database.cli build --db msg_database.db
python -m msg_database.cli msg 1 --db msg_database.db
python -m msg_database.cli operation --rotation ... --translation ... --time-reversal 0 --db msg_database.db
```

期待するテスト:

- `build` で DB ファイルが作られる。
- `msg 1` で JSON または表形式の操作一覧が出る。
- 存在しない MSG ID は非ゼロ終了し、明確なエラーメッセージを出す。

## テスト分類

### unit

高速で、spglib 実データやディスク上の固定 DB に依存しないテスト。

- 正規化
- スキーマ作成
- repository の基本 CRUD
- 入力値検証

### integration

spglib と SQLite を組み合わせるテスト。

- 少数 MSG ID の登録
- MSG から operation への検索
- operation から MSG への検索

### slow

1651 件すべてを扱うテスト。

- 完全 DB 構築
- 件数検証
- 再生成性確認

## 推奨コマンド

開発中は以下を基本にする。

```bash
python -m pip install -e ".[dev]"
pytest -q
pytest -q -m "not slow"
pytest -q --cov=src
ruff check .
ruff format .
mypy src
```

CI では最低限、次を走らせる。

```bash
pytest -q -m "not slow"
ruff check .
mypy src
```

全件 DB 構築テストは時間がかかる可能性があるため、最初は手動または nightly 相当の扱いでよい。

## 実装順序

1. `pyproject.toml` の `dev` extra と `pytest.ini` を追加し、marker を定義する。
2. パッケージ構成を `src/msg_database/` に変更する。
3. import 副作用をなくすテストを追加し、現在のランダム出力を削除する。
4. `schema.py` とスキーマ作成テストを追加する。
5. `normalize.py` と正規化テストを追加する。
6. `repository.py` と検索 API のテストを追加する。
7. `spglib_adapter.py` と少数 MSG ID の統合テストを追加する。
8. `builder.py` で DB 構築処理を実装する。
9. `cli.py` と CLI テストを追加する。
10. 1651 件全体の slow テストを追加する。
11. GitHub Actions を更新し、通常テストと lint を自動化する。

## 完了条件

このプロジェクトは、以下を満たしたら完遂とみなす。

- `pytest -q -m "not slow"` がローカルと CI で成功する。
- `pytest -q -m slow` がローカルで成功する。
- `python -m msg_database.cli build --db data/generated/msg_database.sqlite` で 1651 件の DB を再生成できる。
- `msg_type` に 1651 行が入る。
- 任意の MSG ID から群操作一覧を取得できる。
- 任意の正規化済み群操作から、それを含む MSG ID 一覧を取得できる。
- README にセットアップ、DB 生成、検索コマンド、テスト実行方法が書かれている。

## 注意点

- `data/generated/msg_database.sqlite` のような生成物は Git 管理せず、必要ならリリース成果物として扱う。
- spglib のバージョンで出力形式や順序が変わる可能性があるため、`pyproject.toml` と lock file でバージョン固定を検討する。
- 群操作の順序に意味がない検索では集合として比較する。表示順が必要な場合だけ `operation_order` を使う。
- SQLite の外部キーは接続ごとに `PRAGMA foreign_keys = ON` が必要である。
- テストで `shell=True` は使わない。subprocess を使う場合は引数配列で実行する。
