# tests

テスト全体を置くディレクトリです。

- `unit/`: spglib 実データに依存しない高速な単体テスト。
- `integration/`: spglib と SQLite または CLI を組み合わせた統合テスト。
- `slow/`: 全 1651 MSG など、明示的に実行する重いテストの置き場所。
- `fixtures/`: fake provider や固定入力データを追加する場所。

通常は `pytest -q` を実行します。`pytest.ini` により slow marker は除外されます。
