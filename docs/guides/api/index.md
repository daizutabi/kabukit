# Python API の使い方

kabukit は、複数のソースからデータを取得するための、
Python API 提供します。

現在サポートしているソースは以下の通りです。

- [J-Quants API](https://jpx-jquants.com/)
- [EDINET API](https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html)

## ノートブックでの非同期処理

kabukit は、[httpx](https://www.python-httpx.org/) を使った非同期設計になっており、
[Jupyter](https://jupyter.org/) や [marimo](https://marimo.io/) のような
非同期処理を直接扱えるノートブック環境で快適に利用できます。

## 2 つのインターフェース

Python API は、モジュール関数と Client クラスの 2 のインターフェースを提供します。

### モジュールレベル関数

httpx クライアントを意識することなく、手軽にデータを取得にするのに
適しています。また、銘柄コードや日付を複数指定すると、関数内部で非同期処理を
並列実行するため、効率的に情報を取得できます。

以下の例では、J-Quants API から株価情報を取得します。
`get_prices` 関数に銘柄コードを与えます。

```python .md#_
import polars as pl
pl.Config.set_tbl_cols(None)
```

```python exec="1" source="material-block"
from kabukit import get_prices

df = await get_prices("7203")
df.select("Date", "Code", "Open", "High", "Low", "Close", "Volume")
```

`get_prices` 関数に銘柄コードのリストを与えると、
非同期処理を並列実行して、複数銘柄の株価情報を一度に取得します。

```python exec="1" source="material-block"
import polars as pl
from polars import col as c

# 複数銘柄の株価情報を取得
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

### Client クラス

より詳細な制御（例: タイムアウト設定、リトライポリシーの変更など）
が必要な場合に直接利用します。
特に、各クラスの `client` 属性は `httpx.AsyncClient` のインスタンスであるため、
httpx が提供する豊富なメソッドや設定に直接アクセスすることが可能です。

たとえば、J-Quants API に対応した `JQuantsClient` は以下のように使います。

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
