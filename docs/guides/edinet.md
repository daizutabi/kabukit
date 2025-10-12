# EDINET 利用ガイド

`kabukit` は、`httpx` を使った非同期設計になっており、[Jupyter](https://jupyter.org/) や [marimo](https://marimo.io/) のような非同期処理を直接扱えるノートブック環境で快適に利用できます。

このガイドでは、`EDINETClient` を使った書類検索の方法を解説します。

## 認証とクライアントの準備

API を利用するには、事前に CLI で EDINET の認証情報を設定しておく必要があります。

```bash
kabu auth edinet
```

認証が完了したら、ノートブックで `EDINETClient` をインポートしてインスタンスを作成します。`async with` 構文を使うことで、セッションを安全に管理できます。

```python
from kabukit import EDINETClient

# 非同期で利用する場合
async with EDINETClient() as client:
    # このブロック内で API を呼び出す
    pass
```

## 書類検索

`EDINETClient` を使うと、期間や書類種別コードを指定して、提出された書類のメタデータを検索できます。

```python
from kabukit import EDINETClient
from datetime import date

async def main():
    async with EDINETClient() as client:
        # 2024-01-01 から 2024-01-05 までの有価証券報告書を検索
        docs = await client.search_documents(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 5),
            doc_type_codes=["030000"] # 有価証券報告書
        )
        print(docs)

# Jupyter などトップレベルで await が使える環境では、直接 await してください
# await main()
```
