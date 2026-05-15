# Operation 正規化

`spglib` の symmetry data は、SQLite へ保存する前に正規化します。

- rotation matrix は、内部では行優先の 9 個の整数として保持します。
- translation vector は、内部では分母 24 以内に制限した 3 個の `Fraction` として保持します。
- time reversal は、内部では `bool` として保持します。

SQLite に渡す安定した文字列キーは、repository 層の境界でだけ生成します。

- `rotation_key`: `1,0,0,0,1,0,0,0,1`
- `translation_key`: `0,1/2,0`
- `time_reversal`: `0` または `1`

この分離により、内部ロジックでは型付きの値として比較でき、DB では一意制約に使いやすい文字列として扱えます。
