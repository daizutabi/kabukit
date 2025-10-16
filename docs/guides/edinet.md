# EDINET API の使い方

kabukit は、[httpx](https://www.python-httpx.org/) を使った非同期設計になっており、
[Jupyter](https://jupyter.org/) や [marimo](https://marimo.io/) のような
非同期処理を直接扱えるノートブック環境で快適に利用できます。

このガイドでは、`EdinetClient` を使った書類検索の方法を解説します。

## 認証

API を利用するには、事前にコマンドラインで EDINET API の認証情報を設定しておく必要があります。
詳細は、[コマンドラインインターフェースの使い方](cli.md)の「認証」セクションを参照してください。

環境変数 `EDINET_API_KEY` に直接 API キーを設定することも可能です。

## クライアントの使い方

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

また、クライアントが不要であれば、後述するモジュールレベルの
関数を直接使うことも可能です。

## 書類一覧

`EdinetClient` を使うと、日付を指定して、提出された書類のメタデータを検索できます。

```python .md#_
client = EdinetClient()
```

```python exec="1" source="material-block"
df = await client.get_entries("2025-10-10")
df.select("Date", "Code", "docID", "filerName", "pdfFlag", "csvFlag").tail()
```

## モジュール関数の使い方

モジュールレベル関数の `kabukit.get_entries` 関数を使うことができます。

```python exec="1" source="material-block"
from kabukit import get_entries

df = await get_entries("2025-10-10")
df.select("Date", "Code", "docID", "filerName", "pdfFlag", "csvFlag").tail()
```

複数の提出日の書類一覧を一度に取得することもできます。
このとき、EDINET API へのリクエストは非同期で並列に行われるので、
効率的に情報取得ができます。

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

## 書類本文

モジュールレベル関数の `kabukit.get_documents` 関数を使うことができます。
書類一覧で取得した書類 ID (`docID`) を引数にとります。

```python exec="1" source="material-block"
from kabukit import get_documents

df = await get_documents("S100WUKL")
df.select("docID", "要素ID", "項目名", "値").head()
```

複数の書類 ID を与えて、非同期に並列に取得することもできます。

```python exec="1" source="material-block"
doc_ids = df_years.filter("csvFlag")["docID"]
df = await get_documents(doc_ids, max_items=3)
df.select("docID", "要素ID", "項目名", "値").head()
```

`pdf`キーワードを`True`に指定すると、書類本文をPDF形式で
取得できます。データフレームのカラム名は `"pdf"` で型は、
`polars.Binary`です。バイナリファイルとして保存すれば、
PDF形式で閲覧することができます。

```python .md#_
import polars as pl
pl.Config(fmt_str_lengths=15)
```

```python exec="1" source="material-block"
df = await get_documents(doc_ids, max_items=3, pdf=True)
df.select("docID", "pdf").tail()
```

```python .md#_
pl.Config(fmt_str_lengths=None)
```
