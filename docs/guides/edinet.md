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

### 書類一覧 (`get_list`)

[`EdinetClient.get_list`][kabukit.EdinetClient.get_list]
メソッドは、日付を指定して、提出された書類のメタデータを取得します。

```python .md#_
client = EdinetClient()
```

```python exec="1" source="material-block"
df = await client.get_list("2025-10-10")
df.select("Date", "Code", "DocumentId", "Company", "PdfFlag", "CsvFlag").tail()
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

## DataFrame のカラム名について

kabukit が返す DataFrame のカラム名は、データソース（J-Quants, EDINETなど）によらず、
一貫した命名規則に従うよう設計されています。
これにより、利用者はソースの違いを意識することなく、統一された使いやすいインターフェースでデータを扱うことができます。

### EDINET 特有の変更点

EDINET API から返される lowerCamelCase のフィールド名は、
以下のように PascalCase に変更されます。
doc のような略語は、J-Quants API にあわせて、Document とします。
また、利用者が直感的に理解しにくいカラムは削除されます。

主要なカラムの対応表は以下の通りです。

| EDINET API | kabukit | 説明 |
| :--- | :--- | :--- |
| docID | DocumentId | 書類のユニーク ID |
| secCode | Code | 銘柄コード (J-Quants と統一) |
| filerName | Company | 会社名 (J-Quants と統一) |
| docTypeCode | DocumentTypeCode | 書類種別コード |
| docDescription | DocumentDescription | 書類概要 |
| parentDocID | ParentDocumentId | 親書類の ID |

### kabukit が追加するカラム

kabukit は、利便性のためにAPIレスポンスには含まれないカラムをいくつか追加します。

- FileDate: APIにリクエストした「ファイル日付」。どの日の書類一覧を取得したかを示します。
- SubmittedDate / SubmittedTime: submitDateTime を日付と時刻に分割したものです。
- Date: **（最重要）** 株価への影響を考慮して計算された**実効日**です。
  EDINET の場合、提出時刻 (SubmittedTime) が 15:00 より前であれば提出日当日、
  15:00 以降であれば翌営業日が基準となります。

## Date カラム決定ロジック

### 課題

kabukit ライブラリが提供する Date カラムは、「その情報が株価に影響を与えうる日」を表現することを目的としています。

J-Quants APIには DisclosedDate および DisclosedTime フィールドが存在するため、
15:30 を市場の取引時間後の閾値（スレッショルド）として Date を計算するロジックは比較的単純です。

しかし、EDINET API は submitDateTime（提出日時）しか提供していません。
EDINET の仕様上、「提出」から「開示（利用者が閲覧可能になること）」までには未知のタイムラグが存在するため、
「提出日時＝開示日時」とみなすことはできません。
この不確実性の中で、いかにして信頼性のある Date を決定するかが課題です。

### リスク分析

Date の計算ロジックを設計する上で、考慮すべきリスクは以下の通りです。

- **最も避けるべきリスク:** 本来は翌営業日の株価に影響する情報（例: 15:30 以降に開示された情報）を、
  当日の情報として誤って分類してしまうこと
- **許容されるリスク:** 本来は当日の情報として扱えるもの（例: 14:00に開示された情報）を、
  安全側に倒して翌営業日扱いとしてしまうこと

kabukit では、「本当は翌日扱いなのに当日扱いしてしまう」リスクを最小化する、
**保守的な（conservative）**方針を取ります。

### 解決策：安全マージンの導入

上記のリスク分析に基づき、以下のロジックで Date を決定します。

1. **開示の最終デッドラインを 15:30 と定義する。**
    これは J-Quants における Date の決定ロジックと一貫性を保つためです。
    この時刻までに開示された情報は、当日の株価に影響を与えうるとみなします。

2. **30分の「安全マージン」を設ける。**
    EDINET の「提出から開示までの未知のタイムラグ」を吸収するためのバッファとして、
    30 分という安全マージンを設定します。

3. **提出時刻の閾値を 15:00 に設定する。**
    上記から逆算し、提出時刻 (SubmittedTime) の閾値を 15:30 (デッドライン) － 30 分 (安全マージン) ＝ 15:00 とします。

### 最終的な計算ルール

- EDINET データの SubmittedTime が**15:00より前**の場合、SubmittedDate を Date とします。
- EDINET データの SubmittedTime が**15:00以降**の場合、SubmittedDate の**翌営業日**を Date とします。

このロジックにより、不確実性を許容しつつ、最も合理的で防御可能な方法で Date カラムを導出します。
