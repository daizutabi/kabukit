# J-Quants 利用ガイド

`kabukit` は、`httpx` を使った非同期設計になっており、[Jupyter](https://jupyter.org/) や [marimo](https://marimo.io/) のような非同期処理を直接扱えるノートブック環境で快適に利用できます。

このガイドでは、`JQuantsClient` を使ったデータ取得とキャッシュの活用方法を解説します。

## 認証

API を利用するには、事前にコマンドラインで J-Quants の認証情報を設定しておく必要があります。

```bash
> kabu auth jquants
Mailaddress: your_email@example.com
Password: your_password
J-Quants の ID トークンを保存しました。
```

## クライアントの使い方

ノートブックで `kabukit.JQuantsClient` をインポートしてインスタンスを作成します。

```python exec="1" source="1"
from kabukit import JQuantsClient

client = JQuantsClient()
# ここで API を呼び出す
await client.aclose()  # 最後にセッションを閉じる
```

`async with` 構文を使うことで、セッションを安全に管理できます。

```python exec="1" source="1"
async with JQuantsClient() as client:
    # このブロック内で API を呼び出す
    pass
```

## データ取得

`JQuantsClient` は、さまざまなデータを取得するための非同期メソッドを提供します。
返り値はすべて高速な `polars.DataFrame` です。

### 上場銘柄一覧

`get_info` メソッドは、上場企業の情報を取得します。
J-Quants API の[上場銘柄一覧 (/listed/info)](https://jpx.gitbook.io/j-quants-ja/api-reference/listed_info) に対応します。

```python .md#_
client = JQuantsClient()
```

引数に銘柄コードを指定すると、特定企業の情報を取得できます。

```python exec="1" source="material-block"
df = await client.get_info("7203")
df.select("Date", "Code", "CompanyName").tail()
```

戻り値のカラムは、J-Quants API の[データ項目概要](https://jpx.gitbook.io/j-quants-ja/api-reference/listed_info#dta)に対応します。

銘柄コードを指定して、特定の企業の情報を取得します。

```python
import asyncio
from kabukit import JQuantsClient

async def main():
    async with JQuantsClient() as client:
        # 銘柄情報
        info = await client.get_info("7203")
        print(info)

        # 財務情報
        statements = await client.get_statements("7203")
        print(statements)

        # 株価情報
        prices = await client.get_prices("7203")
        print(prices)

# Jupyter などトップレベルで await が使える環境では、直接 await してください
# await main()
```

### 全銘柄のデータ一括取得

`fetch_all` 関数を使うと、全銘柄のデータを一度に取得できます。
`marimo` のような UI フレームワークと組み合わせることで、進捗状況を可視化することも可能です。

対象となるデータは以下の通りです。

- `info`: 銘柄情報
- `prices`: 株価情報
- `statements`: 財務情報

```python
import marimo as mo
from kabukit.jquants import fetch_all

# 全銘柄の財務情報を取得（marimo のプログレスバーを利用）
statements = await fetch_all("statements", progress=mo.status.progress_bar)

# 全銘柄の株価情報を取得
prices = await fetch_all("prices")
```

## キャッシュの活用

CLI の `kabu get` コマンドで取得・保存されたデータは、キャッシュとしてローカルストレージに保存されています。
ノートブックからは、これらのキャッシュデータを直接読み込むことができます。API へのアクセスが不要になるため、高速に分析を開始できます。

```python
from kabukit import Info, Statements, Prices, ListedIssues

# CLI で取得したキャッシュを読み込む
# .data 属性で Polars DataFrame にアクセスできる
info_df = Info.read().data
statements_df = Statements.read().data
prices_df = Prices.read().data
listed_issues_df = ListedIssues.read().data # 銘柄一覧

print("--- Statements Cache ---")
print(statements_df.head())
```
