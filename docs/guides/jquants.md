# J-Quants API の使い方

kabukit は、[httpx](https://www.python-httpx.org/) を使った非同期設計になっており、
[Jupyter](https://jupyter.org/) や [marimo](https://marimo.io/) のような
非同期処理を直接扱えるノートブック環境で快適に利用できます。

このガイドでは、`JQuantsClient` を使ったデータ取得とキャッシュの活用方法を解説します。

## 認証

API を利用するには、事前にコマンドラインで J-Quants API の認証情報を設定しておく必要があります。

```bash
$ kabu auth jquants
Mailaddress: my_email@example.com
Password: my_password
J-QuantsのIDトークンを保存しました。
```

## クライアントの使い方

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

## データ取得

`JQuantsClient` は、さまざまなデータを取得するための非同期メソッドを提供します。
返り値はすべて高速な `polars.DataFrame` です。

### 上場銘柄一覧

`get_info` メソッドは、上場企業の情報を取得します。
J-Quants API の[上場銘柄一覧 (/listed/info)](https://jpx.gitbook.io/j-quants-ja/api-reference/listed_info)
に対応します。

```python .md#_
client = JQuantsClient()
```

引数に銘柄コードを指定すると、特定企業の情報を取得できます。

```python exec="1" source="material-block"
df = await client.get_info("7203")
df.select("Date", "Code", "CompanyName")
```

戻り値のカラムは、J-Quants API の
[データ項目概要](https://jpx.gitbook.io/j-quants-ja/api-reference/listed_info#dta)
に対応します。

引数を省略すると、全企業の情報を取得できます。

```python exec="1" source="material-block"
df = await client.get_info()
df.select("Date", "Code", "CompanyName").tail()
```

```python exec="1" source="material-block"
df.shape
```

### 財務情報

`get_statements` メソッドは、四半期の財務情報を取得します。
J-Quants API の[財務情報 (/fins/statements)](https://jpx.gitbook.io/j-quants-ja/api-reference/statements)
に対応します。

引数に銘柄コードを指定すると、特定企業の情報を取得できます。

```python exec="1" source="material-block"
df = await client.get_statements("7203")
df.select("DisclosedDate", "Code", "TypeOfDocument", "Profit").tail()
```

戻り値のカラムは、J-Quants API の
[データ項目概要](https://jpx.gitbook.io/j-quants-ja/api-reference/statements#dta)
に対応します。
ただし、分析を行いやすくするために、株式数に関して以下の変更を行っています。

- 期末発行済株式数（自己株式を含む）
    - （変更前）NumberOfIssuedAndOutstandingSharesAtTheEndOfFiscalYearIncludingTreasuryStock
    - （変更後）IssuedShares
- 期末自己株式数
    - （変更前）NumberOfTreasuryStockAtTheEndOfFiscalYear
    - （変更後）TreasuryShares
- 期中平均株式数（自己株式を含まない）
    - （変更前）AverageNumberOfShares
    - （変更後）AverageOutstandingShares

引数に日付を指定すると、該当する開示日の情報をまとめて取得できます。

```python exec="1" source="material-block"
df = await client.get_statements(date="2025-10-10")
df.select("DisclosedDate", "Code", "TypeOfDocument", "Profit").head()
```

複数の企業の情報を一度に取得するには、`fetch`関数を使います。

```python exec="1" source="material-block"
import polars as pl
from kabukit.jquants import fetch

df = await fetch("statements", ["7203", "9984", "8306", "6758"])
df.group_by("Code").agg(pl.len(), pl.col("Equity").max())
```

### 株価情報

`get_prices` メソッドは、株価情報を取得します。
J-Quants API の[株価四本値 (/prices/daily_quotes)](https://jpx.gitbook.io/j-quants-ja/api-reference/daily_quotes)
に対応します。

引数に銘柄コードを指定すると、特定企業の情報を取得できます。

```python exec="1" source="material-block"
df = await client.get_prices("7203")
df.select("Date", "Code", "Open", "High", "Low", "Close", "Volume").tail()
```

戻り値のカラムは、J-Quants API の
[データ項目概要](https://jpx.gitbook.io/j-quants-ja/api-reference/daily_quotes#dta)
に対応します。
ただし、分析を行いやすくするために、株価などの調整に関して以下の変更を行っています。

| J-Quants API | kabukit | 説明 |
| :--: | :--: | :--: |
| Open | RawOpen | 始値（調整前） |
| High | RawHigh | 高値（調整前） |
| Low | RawLow | 安値（調整前） |
| Close | RawClose | 終値（調整前） |
| Volume | RawVolume | 取引高（調整前） |
| AdjustmentOpen | Open | 調整済み始値 |
| AdjustmentHigh | High | 調整済み高値 |
| AdjustmentLow | Low | 調整済み安値 |
| AdjustmentClose | Close | 調整済み終値 |
| AdjustmentVolume | Volume | 調整済み取引高 |

引数に日付を指定すると、該当する取引日の情報をまとめて取得できます。

```python exec="1" source="material-block"
df = await client.get_prices(date="2025-10-10")
df.select("Date", "Code", "Open", "High", "Low", "Close", "Volume").tail()
```

複数の企業の情報を一度に取得するには、`fetch`関数を使います。

```python exec="1" source="material-block"
from polars import col as c

df = await fetch("prices", ["7203", "9984", "8306", "6758"])
df.group_by(c.Code).agg(pl.len(), c.Date.last(), c.Close.last())
```

## 全企業のデータ取得

`fetch_all` 関数を使うと、全銘柄のデータを一度に取得できます。
`marimo` のような UI フレームワークと組み合わせることで、
進捗状況を可視化することも可能です。

```python
import marimo as mo
from kabukit.jquants import fetch_all

# 全銘柄の財務情報を取得（marimo のプログレスバーを利用）
df = await fetch_all("statements", progress=mo.status.progress_bar)

# 全銘柄の株価情報を取得
df = await fetch_all("prices")
```

参考までに、10 年分の全銘柄の情報を取得するのに
要する時間、および、戻り値の DataFrame の行数は以下のとおりです。

- 財務情報 (`"statements"`)：約 70 秒、約 16 万行
- 株価情報 (`"prices"`)：約 12 分、約 8 百万行

このように、httpx の非同期アクセスのおかげて、
大量のデータを高速に取得できます。

## キャッシュの活用

CLI の `kabu get` コマンドで取得・保存されたデータは、
キャッシュとしてローカルストレージに保存されています。
ノートブックからは、これらのキャッシュデータを直接読み込むことができます。
J-Quants API へのウェブアクセスが不要になるため、分析をすぐに開始できます。

```python
from kabukit import Info, Statements, Prices

# CLI で取得したキャッシュを読み込む
# .data 属性で Polars DataFrame にアクセスできる
info_df = Info.read().data
statements_df = Statements.read().data
prices_df = Prices.read().data
```
