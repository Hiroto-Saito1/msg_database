# パッケージングとリリース

このプロジェクトは、`msg-database` という Python package として配布できるように準備しています。

## ローカルでの build 確認

source distribution と wheel を作成します。

```bash
.venv/bin/python -m build
```

作成した配布物の metadata を検証します。

```bash
.venv/bin/python -m twine check --strict dist/*
```

PyPI へ公開する前に、clean な仮想環境へ wheel をインストールして CLI が動くことを確認します。

```bash
python3.11 -m venv /tmp/msg-database-wheel-test
/tmp/msg-database-wheel-test/bin/python -m pip install --upgrade pip
/tmp/msg-database-wheel-test/bin/python -m pip install dist/msg_database-0.1.0-py3-none-any.whl
/tmp/msg-database-wheel-test/bin/msg-database --help
```

## PyPI project 名

初回公開の直前に、`msg-database` という project 名が PyPI でまだ使えるか確認します。

```bash
python -m pip index versions msg-database
```

すでに使われている場合は、公開前に `pyproject.toml` の `[project].name` を変更します。

## Trusted Publishing

release workflow は PyPI Trusted Publishing を使う前提です。長期有効な PyPI API token を GitHub secrets に保存しない運用にします。

workflow を実行する前に、PyPI と TestPyPI 側で trusted publisher を設定します。

- Repository: `Hiroto-Saito1/msg_database`
- Workflow: `release.yml`
- TestPyPI 用 environment: `testpypi`
- PyPI 用 environment: `pypi`

本番 PyPI へ公開する environment には、GitHub environments の manual approval を設定するのが安全です。

## リリース手順

1. `CHANGELOG.md` を更新する。
2. `pyproject.toml` の `version` を更新する。
3. release 変更を commit する。
4. `v0.1.0` のような tag を作成して push する。
5. GitHub Actions が配布物を build し、Trusted Publishing 経由で PyPI へ publish する。

TestPyPI への手動 publish は、`Publish Python package` workflow の `workflow_dispatch` trigger から実行できます。
