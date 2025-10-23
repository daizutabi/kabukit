# J-Quants API の使い方

kabukit は、[httpx](https://www.python-httpx.org/) を使った非同期設計になっており、
[Jupyter](https://jupyter.org/) や [marimo](https://marimo.io/) のような
非同期処理を直接扱えるノートブック環境で快適に利用できます。

このガイドでは、kabukit が提供する高レベルなモジュール関数と、
より詳細な制御が可能な [`JQuantsClient`][kabukit.JQuantsClient]
の使い方を解説します。

## 認証設定

API を利用するには、事前にコマンドラインで J-Quants API の ID トークンを取得
しておく必要があります。
詳細は、[CLIの使い方](cli.md)の「認証設定」セクションを参照してください。

## モジュールレベル関数

kabukit は、手軽に J-Quants API からデータを取得できるモジュールレベル関数を提供します。
これらの関数は内部で非同期処理を並列実行するため、効率的に情報を取得できます。

### 上場銘柄一覧 (`get_info`)

[`kabukit.get_info`][] 関数は、上場銘柄の情報を取得します。

銘柄コード (4 桁または 5 桁の文字列) を指定すると、指定した銘柄の情報を取得できます。

```python exec="1" source="material-block"
from kabukit import get_info

df = await get_info("7203")  # または "72030"
df.select("Date", "Code", "CompanyName", "MarketCodeName")
```

銘柄コードを省略すると、全上場銘柄の情報を取得できます。
ただし、デフォルトでは、投資信託や優先株式を除きます。

```python exec="1" source="material-block"
df = await get_info()  # 全上場銘柄一覧を取得 (投資信託や優先株式を除く)
df.select("Date", "Code", "CompanyName", "MarketCodeName")
```

`only_common_stocks` キーワード引数を `False` に設定すると、
J-Quants API から取得できる全銘柄が含まれます。

```python exec="1" source="material-block"
from polars import col as c

df = await get_info(only_common_stocks=False)  # 全上場銘柄一覧を取得
df = df.filter(c.Sector17CodeName == "その他")  # 業種区分が「その他」の銘柄を選択
df.select("Date", "Code", "CompanyName")
```

### 財務情報 (`get_statements`)

[`kabukit.get_statements`][] 関数は、
企業の四半期毎の決算短信サマリーや業績・配当情報の修正に関する
開示情報（主に数値データ）を取得します。

銘柄コードを指定すると、指定した銘柄の全期間分の財務情報を取得できます。

```python exec="1" source="material-block"
from kabukit import get_statements

df = await get_statements("7203")
df.select("DisclosedDate", "Code", "TypeOfDocument")
```

銘柄コードのリストを指定すると、複数銘柄の全期間分の財務情報を一度に取得できます。
このとき、J-Quants API へのリクエストは非同期で並列に行われます。

```python exec="1" source="material-block"
import polars as pl

# 複数銘柄の財務情報を取得
df = await get_statements(["7203", "9984", "8306", "6758"])

# 銘柄コードごとに集計
df.group_by(c.Code).agg(
    pl.len().alias("財務情報の数"),
    c.DisclosedDate.first().alias("初回開示日"),
    c.DisclosedDate.last().alias("最終開示日"),
)
```

銘柄コードを指定しない場合、全銘柄の財務情報を全期間に渡って取得します。
データ量が大きくなるため、コマンドラインインターフェースの利用を推奨します。
ノートブックで試す場合は、`max_items` で取得する銘柄数を制限できます。
また、`progress` に marimo のプログレスバーを指定することで、
進捗を可視化することができます。

```python exec="1" source="material-block"
import marimo as mo

# 最初の3銘柄だけ取得。その際、プログレスバーを表示
df = await get_statements(max_items=3, progress=mo.status.progress_bar)
df.group_by(c.Code).agg(pl.len())
```

### 株価情報 (`get_prices`)

[`kabukit.get_prices`][] 関数は、株価情報を取得します。

株価情報は、分割・併合を考慮した調整済み株価（小数点第２位四捨五入）と
調整前の株価の両方を含みます。

銘柄コードを指定すると、指定した銘柄の全期間分の株価情報を取得できます。

```python .md#_
pl.Config.set_tbl_cols(None)
```

```python exec="1" source="material-block"
from kabukit import get_prices

df = await get_prices("7203")
df.select("Date", "Code", "Open", "High", "Low", "Close", "Volume")
```

銘柄コードのリストを指定すると、複数銘柄の全期間分の株価情報を一度に取得できます。

```python exec="1" source="material-block"
df = await get_prices(["7203", "9984", "8306", "6758"])

# 銘柄コードごとに集計
df.group_by(c.Code).agg(
    pl.len().alias("日数"),
    c.Low.min().alias("最安値"),
    c.High.max().alias("最高値"),
    c.Close.last().alias("直近終値"),
    c.TurnoverValue.mean().alias("1日あたり平均取引代金"),
)
```

銘柄コードを指定しない場合、全銘柄の株価情報を全期間に渡って取得します。
データ量が非常に大きくなるため、コマンドラインインターフェースの利用を推奨します。
ノートブックで試す場合は、`max_items` で取得する銘柄数を制限できます。
また、`progress` に marimo のプログレスバーを指定することで、
進捗を可視化することができます。

```python exec="1" source="material-block"
# 最初の3銘柄だけ取得。その際、プログレスバーを表示
df = await get_prices(max_items=3, progress=mo.status.progress_bar)
df.group_by(c.Code).agg(pl.len())
```

## JQuantsClient

[`JQuantsClient`][kabukit.JQuantsClient] の各メソッドは、
[J-Quants APIの仕様](https://jpx.gitbook.io/j-quants-ja/api-reference)
に対応した実装となっています。
また、より詳細な制御（例: タイムアウト設定、リトライポリシーの変更など）
が必要な場合に直接利用します。
特に、`JQuantsClient.client` 属性は `httpx.AsyncClient` のインスタンスであるため、
httpx が提供する豊富なメソッドや設定に直接アクセスすることが可能です。

ノートブックで `kabukit.JQuantsClient` をインポートしてインスタンスを作成します。

```python exec="1" source="1"
from kabukit import JQuantsClient

client = JQuantsClient()
# ここで API を呼び出す
await client.aclose()  # 最後に手動でセッションを閉じる
```

`async with` 構文を使うことで、セッションを安全に管理できます。

```python exec="1" source="1"
async with JQuantsClient() as client:
    # このブロック内で API を呼び出す
    pass
# 自動でセッションが閉じられる
```

### 上場銘柄一覧 (`get_info`)

[`JQuantsClient.get_info`][kabukit.JQuantsClient.get_info]
メソッドは、上場銘柄の情報を取得します。
J-Quants API の[上場銘柄一覧 (/listed/info)](https://jpx.gitbook.io/j-quants-ja/api-reference/listed_info)
に対応します。

引数に銘柄コードを指定して、指定した銘柄の情報を取得します。
実行した日付あるいは翌営業日の情報となります。

```python exec="1" source="material-block"
from kabukit import JQuantsClient

client = JQuantsClient()

df = await client.get_info("7203")  # トヨタ自動車
df.select("Date", "Code", "CompanyName", "Sector17CodeName")
```

`date` 引数に日付を指定して、指定した日付の全銘柄情報を取得します。

```python exec="1" source="material-block"
df = await client.get_info(date="2020-10-01")
df.select("Date", "Code", "CompanyName", "Sector17CodeName")
```

引数を指定しない場合、実行した日付の全銘柄情報を取得します。

```python exec="1" source="material-block"
df = await client.get_info()
df.select("Date", "Code", "CompanyName", "Sector33CodeName")
```

全銘柄情報の取得では、デフォルトでは、投資信託や優先株式は除外されます。
J-Quants API から取得できる全銘柄を取得するには、
`only_common_stocks` キーワード引数を `False` に設定します。

```python exec="1" source="material-block"
df = await client.get_info(only_common_stocks=False)
df = df.filter(c.Sector17CodeName == "その他")  # 業種区分が「その他」の銘柄を選択
df.select("Date", "Code", "CompanyName")
```

### 財務情報 (`get_statements`)

[`JQuantsClient.get_statements`][kabukit.JQuantsClient.get_statements]
メソッドは、
企業の四半期毎の決算短信サマリーや業績・配当情報の修正に関する
開示情報（主に数値データ）を取得します。
J-Quants API の[財務情報 (/fins/statements)](https://jpx.gitbook.io/j-quants-ja/api-reference/statements)
に対応します。

引数に銘柄コードを指定して、指定した銘柄の全期間分の財務情報を取得します。

```python exec="1" source="material-block"
df = await client.get_statements("7203") # トヨタ自動車
df.select("DisclosedDate", "Code", "TypeOfDocument", "NetSales", "Profit")
```

`date` 引数に日付を指定して、指定した日付に開示された財務情報を取得します。

```python exec="1" source="material-block"
df = await client.get_statements(date="2025-10-16")
df.select("DisclosedDate", "Code", "TypeOfDocument", "Profit", "ForecastProfit")
```

### 株価情報 (`get_prices`)

[`JQuantsClient.get_prices`][kabukit.JQuantsClient.get_prices]
メソッドは、株価情報を取得します。
J-Quants API の[株価四本値 (/prices/daily_quotes)](https://jpx.gitbook.io/j-quants-ja/api-reference/daily_quotes)
に対応します。

株価情報は、分割・併合を考慮した調整済み株価（小数点第２位四捨五入）と
調整前の株価の両方を含みます。

引数に銘柄コードを指定して、指定した銘柄の全期間分の株価情報を取得します。

```python exec="1" source="material-block"
df = await client.get_prices("7203") # トヨタ自動車
df.select("Date", "Code", "Open", "High", "Low", "Close", "Volume")
```

`date` 引数に日付を指定して、全上場銘柄について指定された日付の株価情報を取得します。

```python exec="1" source="material-block"
df = await client.get_prices(date="2025-10-17")
df.select("Date", "Code", "Open", "High", "Low", "Close", "Volume")
```

`from_`, `to` 引数で期間を指定することもできます。
このとき銘柄コードは必須です。

```python exec="1" source="material-block"
df = await client.get_prices("7203", from_="2025-01-01", to="2025-05-31")

# 月次の株価四本値を求める
df.group_by(c.Date.dt.truncate("1mo"), c.Code).agg(
    c.Open.first(),
    c.High.max(),
    c.Low.min(),
    c.Close.last(),
    c.Volume.sum(),
).sort(c.Code, c.Date)
```

## DataFrameのカラム名について

J-Quants API から返される JSON 形式のデータは、
`JQuantsClient`クラスの各メソッドで Polars DataFrame に変換されます。
その際、後続の分析を行いやすくするために、一部のカラム名が変更されます。

### 財務情報

株式数に関するカラム名は、
文字数を短縮するため、および、意味を明確にするために、
以下のように変更されます。

- 期末発行済株式数（自己株式を含む）
    - （変更前）NumberOfIssuedAndOutstandingSharesAtTheEndOfFiscalYearIncludingTreasuryStock
    - （変更後）IssuedShares
- 期末自己株式数
    - （変更前）NumberOfTreasuryStockAtTheEndOfFiscalYear
    - （変更後）TreasuryShares
- 期中平均株式数（自己株式を含まない）
    - （変更前）AverageNumberOfShares
    - （変更後）AverageOutstandingShares

### 株価情報

株価に関するカラム名が以下のように変更されます。

- J-Quants API では、調整済みの値に `Adjustment` プレフィックス
  を付けています。kabukit ではカラム名を単純化するために、
  プレフィックスのない `Open`, `Close` などで、調整済みの値を表します。
- `Raw` プレフィックスが付いているものが、調整前の実際に取引に使われた値です。

下に対応表を示します。

| J-Quants API | kabukit | 説明 |
| :--: | :--: | :--: |
| AdjustmentOpen | Open | 調整済み始値 |
| AdjustmentHigh | High | 調整済み高値 |
| AdjustmentLow | Low | 調整済み安値 |
| AdjustmentClose | Close | 調整済み終値 |
| AdjustmentVolume | Volume | 調整済み取引高 |
| Open | RawOpen | 始値（調整前） |
| High | RawHigh | 高値（調整前） |
| Low | RawLow | 安値（調整前） |
| Close | RawClose | 終値（調整前） |
| Volume | RawVolume | 取引高（調整前） |
