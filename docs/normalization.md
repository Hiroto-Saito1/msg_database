# Operation normalization

`spglib` symmetry data is normalized before insertion.

- Rotation matrices are stored internally as 9 integer values in row-major order.
- Translation vectors are stored internally as three `Fraction` values limited to denominator 24.
- Time reversal is stored internally as `bool`.

SQLite receives stable text keys only at the repository boundary:

- `rotation_key`: `1,0,0,0,1,0,0,0,1`
- `translation_key`: `0,1/2,0`
- `time_reversal`: `0` or `1`
