# EDINET API の使い方

kabukit は、[httpx](https://www.python-httpx.org/) を使った非同期設計になっており、
[Jupyter](https://jupyter.org/) や [marimo](https://marimo.io/) のような
非同期処理を直接扱えるノートブック環境で快適に利用できます。

このガイドでは、kabukit が提供する高レベルなモジュール関数と、
より詳細な制御が可能な [`EdinetClient`][kabukit.EdinetClient] の使い方を解説します。

## 認証設定

API を利用するには、事前にコマンドラインで EDINET API の API キーを設定しておく必要があります。
詳細は、[CLIの使い方](cli.md)の「認証設定」セクションを参照してください。

環境変数 `EDINET_API_KEY` に直接 API キーを設定することも可能です。

## モジュールレベル関数

kabukit は、手軽に EDINET API からデータを取得できるモジュールレベル関数を提供します。
これらの関数は内部で非同期処理を並列実行するため、効率的に情報を取得できます。

### 書類一覧 (`get_entries`)

[`kabukit.get_entries`][] 関数は、提出書類一覧を取得します。

日付 (YYYY-MM-DD) を指定すると、指定した日付に提出された書類一覧を取得できます。

```python exec="1" source="material-block"
from kabukit import get_entries

df = await get_entries("2025-10-10")
df.select("Date", "Code", "docID", "filerName", "pdfFlag", "csvFlag").tail()
```

複数の提出日の書類一覧を一度に取得することもできます。
このとき、EDINET API へのリクエストは非同期で並列に行われます。

```python exec="1" source="material-block"
df = await get_entries(["2025-10-10", "2025-10-14", "2025-10-15"])
df.select("Date", "Code", "docID", "filerName", "pdfFlag", "csvFlag").tail()
```

戻り値のデータフレームは、銘柄コード (`Code`)、日付 (`Date`) の順でソートされます。

過去のある日数あるいは年数に渡る提出日の書類一覧を取得することもできます。

```python exec="1" source="material-block"
df = await get_entries(days=10)
df.select("Date", "Code", "docID", "filerName", "pdfFlag", "csvFlag").head()
```

```python exec="1" source="material-block"
df_years = await get_entries(years=1)
df_years.select("Date", "Code", "docID", "filerName", "pdfFlag", "csvFlag").head()
```

### 書類本文 (`get_documents`)

[`kabukit.get_documents`][] 関数は、書類本文を取得します。
書類一覧で取得した書類 ID (`docID`) を引数にとります。

```python exec="1" source="material-block"
from kabukit import get_documents

df = await get_documents("S100WUKL")
df.select("docID", "要素ID", "項目名", "値").head()
```

複数の書類 ID を与えて、非同期に並列取得することもできます。

```python exec="1" source="material-block"
from polars import col as c

doc_ids = df_years.filter(c.csvFlag)["docID"]  # CSV形式を提供する書類を選択
df = await get_documents(doc_ids, max_items=3)
df.select("docID", "要素ID", "項目名", "値").head()
```

!!! info
    EDINETの書類は、すべてが CSV 形式 (XBRL) で提供されるわけではありません。
    `csvFlag` が `True` の書類のみ、表形式の構造化データとして取得できます。

`pdf` キーワード引数を `True` に指定すると、書類本文を PDF 形式で
取得できます。
データフレームのカラム名は `"pdf"`、データ型は `polars.Binary` です。
バイナリファイルとして保存すれば、PDF 形式の書類を閲覧することができます。

```python .md#_
import polars as pl
pl.Config(fmt_str_lengths=15)
```

```python exec="1" source="material-block"
doc_ids = df_years.filter(c.pdfFlag)["docID"]  # PDF形式を提供する書類を選択
df = await get_documents(doc_ids, max_items=3, pdf=True)
df.select("docID", "pdf").tail()
```

```python .md#_
pl.Config(fmt_str_lengths=None)
```

!!! info
    EDINETの書類は、すべてが PDF 形式で提供されるわけではありません。
    `pdfFlag` が `True` の書類のみ、PDF の原本を取得できます。

## EdinetClient

[`EdinetClient`][kabukit.EdinetClient] は、
より詳細な制御（例: タイムアウト設定、リトライポリシーの変更など）
が必要な場合に直接利用します。
特に、`EdinetClient.client` 属性は `httpx.AsyncClient` のインスタンスであるため、
httpx が提供する豊富なメソッドや設定に直接アクセスすることが可能です。

ノートブックで `kabukit.EdinetClient` をインポートしてインスタンスを作成します。

```python exec="1" source="1"
from kabukit import EdinetClient

client = EdinetClient()
# ここで API を呼び出す
await client.aclose()  # 最後に手動でセッションを閉じる
```

`async with` 構文を使うことで、セッションを安全に管理できます。

```python exec="1" source="1"
async with EdinetClient() as client:
    # このブロック内で API を呼び出す
    pass
# 自動でセッションが閉じられる
```

### 書類一覧 (`get_entries`)

[`EdinetClient.get_entries`][kabukit.EdinetClient.get_entries]
メソッドは、日付を指定して、提出された書類のメタデータを取得します。

```python .md#_
client = EdinetClient()
```

```python exec="1" source="material-block"
df = await client.get_entries("2025-10-10")
df.select("Date", "Code", "docID", "filerName", "pdfFlag", "csvFlag").tail()
```

### 書類本文 (`get_document`)

[`EdinetClient.get_document`][kabukit.EdinetClient.get_document]
メソッドは、文書 ID を指定して、書類本文を取得します。

```python exec="1" source="material-block"
df = await client.get_document("S100WUKL")
df.select("docID", "要素ID", "項目名", "値").head()
```

`pdf` キーワード引数を `True` に指定すると、書類本文を PDF 形式で
取得できます。

```python .md#_
pl.Config(fmt_str_lengths=15)
```

```python exec="1" source="material-block"
df = await client.get_document("S100WUKL", pdf=True)
df.select("docID", "pdf").tail()
```

```python .md#_
pl.Config(fmt_str_lengths=None)
```

!!! note
    モジュール関数は複数の書類を一度に取得できるので、`get_documents`（複数形）です。
    一方、`EdinetClient` のメソッドは単一の書類を取得するので、
    `get_document`（単数形）です。

## データ形式について

[`kabukit.get_documents`][] 関数および
[`EdinetClient.get_document`][kabukit.EdinetClient.get_document] メソッドで
取得される書類本文は、EDINET が提供する CSV 形式のデータ（元のデータは XBRL 形式）を
Polars DataFrame に変換したものです。
