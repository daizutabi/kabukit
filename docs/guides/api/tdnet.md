# TDnet

このガイドでは、kabukit が提供する高レベルなモジュール関数と、
より詳細な制御が可能な [`TdnetClient`][kabukit.TdnetClient] の使い方を解説します。

## モジュールレベル関数

### 書類一覧 (`get_tdnet_list`)

[`kabukit.get_tdnet_list`][] 関数は、適時開示情報の書類一覧を取得します。

日付（YYYYMMDD または YYYY-MM-DD）を指定すると、指定した日に開示された書類一覧を取得できます。

```python exec="1" source="material-block"
from kabukit import get_tdnet_list

df = await get_tdnet_list("20251010")
df.select("Date", "Code", "Company", "Title").tail()
```

複数の日付の書類一覧を一度に取得することもできます。
このとき、TDnet へのリクエストは非同期で並列に行われます。

```python exec="1" source="material-block"
df = await get_tdnet_list(["2025-10-10", "2025-10-14", "2025-10-15"])
df.select("Date", "Code", "Company", "Title").tail()
```

戻り値のデータフレームは、銘柄コード (`Code`)、日付 (`Date`) の順でソートされます。

## TdnetClient

`kabukit.TdnetClient` をインポートしてインスタンスを作成します。

```python exec="1" source="1"
from kabukit import TdnetClient

client = TdnetClient()
```

### 書類一覧 (`get_list`)

[`TdnetClient.get_list`][kabukit.TdnetClient.get_list]
メソッドは、日付を指定して、開示された書類のメタデータを取得します。

```python exec="1" source="material-block"
df = await client.get_list("2025-10-10")
df.select("DisclosedDate", "Code", "Company", "Title").tail()
```
