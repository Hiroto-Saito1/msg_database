# src/msg_database/providers

MSG 元データの取得元を抽象化するディレクトリです。

`base.py` の `MsgDataProvider` protocol に合わせれば、builder は spglib 以外の provider でも動作します。実データ取得は `spglib_provider.py` が担当します。
