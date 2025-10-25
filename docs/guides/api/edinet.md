# EDINET API

このガイドでは、kabukit が提供する高レベルなモジュール関数と、
より詳細な制御が可能な [`EdinetClient`][kabukit.EdinetClient] の使い方を解説します。

## 認証設定

EDINET API を利用するには、事前にコマンドラインで EDINET API の API キーを設定しておく必要があります。
詳細は、[CLIの使い方](../cli.md)の「認証設定」セクションを参照してください。

環境変数 `EDINET_API_KEY` に直接 API キーを設定することも可能です。

## モジュールレベル関数

### 書類一覧 (`get_edinet_list`)

[`kabukit.get_edinet_list`][] 関数は、提出書類一覧を取得します。

日付 (YYYY-MM-DD) を指定すると、指定した日付に提出された書類一覧を取得できます。

```python exec="1" source="material-block"
from kabukit import get_edinet_list

df = await get_edinet_list("2025-10-10")
df.select("Date", "Code", "DocumentId", "Company", "PdfFlag", "CsvFlag").tail()
```

複数の提出日の書類一覧を一度に取得することもできます。
このとき、EDINET API へのリクエストは非同期で並列に行われます。

```python exec="1" source="material-block"
df = await get_edinet_list(["2025-10-10", "2025-10-14", "2025-10-15"])
df.select("Date", "Code", "DocumentId", "Company", "PdfFlag", "CsvFlag").tail()
```

戻り値のデータフレームは、銘柄コード (`Code`)、日付 (`Date`) の順でソートされます。

過去のある日数または年数に渡る提出日の書類一覧を取得することもできます。

```python exec="1" source="material-block"
df = await get_edinet_list(days=10)
df.select("Date", "Code", "DocumentId", "Company", "PdfFlag", "CsvFlag").head()
```

```python exec="1" source="material-block"
df_years = await get_edinet_list(years=1)
df_years.select("Date", "Code", "DocumentId", "Company", "PdfFlag", "CsvFlag").head()
```

### 書類本文 (`get_edinet_documents`)

[`kabukit.get_edinet_documents`][] 関数は、書類本文を取得します。
書類一覧で取得した書類 ID (`docID`) を引数にとります。

```python exec="1" source="material-block"
from kabukit import get_edinet_documents

df = await get_edinet_documents("S100WUKL")
df.select("DocumentId", "要素ID", "項目名", "値").head()
```

複数の書類 ID を与えて、非同期に並列取得することもできます。

```python exec="1" source="material-block"
from polars import col as c

doc_ids = df_years.filter(c.CsvFlag)["DocumentId"]  # CSV形式を提供する書類を選択
df = await get_edinet_documents(doc_ids, max_items=3)
df.select("DocumentId", "要素ID", "項目名", "値").head()
```

!!! info
    EDINETの書類は、すべてが CSV 形式 (XBRL) で提供されるわけではありません。
    `csvFlag` が `True` の書類のみ、表形式の構造化データとして取得できます。

`pdf` キーワード引数を `True` に指定すると、書類本文を PDF 形式で
取得できます。
データフレームのカラム名は `"PdfContent"`、データ型は `polars.Binary` です。
バイナリファイルとして保存すれば、PDF 形式の書類を閲覧することができます。

```python .md#_
import polars as pl
pl.Config(fmt_str_lengths=15)
```

```python exec="1" source="material-block"
doc_ids = df_years.filter(c.PdfFlag)["DocumentId"]  # PDF形式を提供する書類を選択
df = await get_edinet_documents(doc_ids, max_items=3, pdf=True)
df.select("DocumentId", "PdfContent").tail()
```

```python .md#_
pl.Config(fmt_str_lengths=None)
```

!!! info
    EDINETの書類は、すべてが PDF 形式で提供されるわけではありません。
    `pdfFlag` が `True` の書類のみ、PDF の原本を取得できます。

## EdinetClient

[`EdinetClient`][kabukit.EdinetClient] の各メソッドは、
[EDINET APIの仕様](https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/download/ESE140206.pdf)
に対応した実装となっています。

`kabukit.EdinetClient` をインポートしてインスタンスを作成します。

```python exec="1" source="1"
from kabukit import EdinetClient

client = EdinetClient()
```

### 書類一覧 (`get_list`)

[`EdinetClient.get_list`][kabukit.EdinetClient.get_list]
メソッドは、日付を指定して、提出された書類のメタデータを取得します。

```python exec="1" source="material-block"
df = await client.get_list("2025-10-10")
df.select("FileDate", "Code", "DocumentId", "Company", "PdfFlag", "CsvFlag").tail()
```

### 書類本文 (`get_document`)

[`EdinetClient.get_document`][kabukit.EdinetClient.get_document]
メソッドは、文書 ID を指定して、書類本文を取得します。

```python exec="1" source="material-block"
df = await client.get_document("S100WUKL")
df.select("DocumentId", "要素ID", "項目名", "値").head()
```

`pdf` キーワード引数を `True` に指定すると、書類本文を PDF 形式で
取得できます。

```python .md#_
pl.Config(fmt_str_lengths=15)
```

```python exec="1" source="material-block"
df = await client.get_document("S100WUKL", pdf=True)
df.select("DocumentId", "PdfContent").tail()
```

```python .md#_
pl.Config(fmt_str_lengths=None)
```

!!! note
    モジュール関数は複数の書類を一度に取得できるので、`get_edinet_documents`（複数形）です。
    一方、`EdinetClient` のメソッドは単一の書類を取得するので、
    `get_document`（単数形）です。

## データ形式について

[`kabukit.get_edinet_documents`][] 関数および
[`EdinetClient.get_document`][kabukit.EdinetClient.get_document] メソッドで
取得される書類本文は、EDINET が提供する CSV 形式のデータ（元のデータは XBRL 形式）を
Polars DataFrame に変換したものです。
