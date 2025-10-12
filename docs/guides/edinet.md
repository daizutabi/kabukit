# EDINET API 利用ガイド

kabukit は、[httpx](https://www.python-httpx.org/) を使った非同期設計になっており、
[Jupyter](https://jupyter.org/) や [marimo](https://marimo.io/) のような
非同期処理を直接扱えるノートブック環境で快適に利用できます。

このガイドでは、`EdinetClient` を使った書類検索の方法を解説します。

## 認証とクライアントの準備

API を利用するには、事前にコマンドラインで EDINET API の認証情報を設定しておく必要があります。

```bash
kabu auth edinet
```

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

## 書類検索

`EdinetClient` を使うと、日付を指定して、提出された書類のメタデータを検索できます。

```python .md#_
client = EdinetClient()
```

```python exec="1" source="material-block"
df = await client.get_documents("2025-10-10")
df.select("Date", "Code", "docID", "filerName", "pdfFlag", "csvFlag").tail()
```

```python exec="1" source="material-block"
df.columns
```
