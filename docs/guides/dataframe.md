# DataFrame

kabukit が返す DataFrame のカラム名は、データソース（J-Quants, EDINET など）によらず、
一貫した命名規則に従うよう設計されています。
J-Quants API の仕様にならって、全てのカラム名は PascalCase で記述されます。
これにより、ユーザーはソースの違いを意識することなく、統一された使いやすいインターフェースでデータを扱うことができます。

## J-Quants API

J-Quants API から返される JSON データを DataFrame に変換する際、
続く分析を行いやすくするために、一部のカラム名が変更されます。

### 銘柄情報

Sector17Code, Sector17CodeName のような、コード値と名前の両方があるカラムでは、
重複をさけるために、コード値のカラムを削除し、名前のカラムは、より簡潔な Sector17 などに変更します。
また、一貫性のために、CompanyName を Company に変更します。

### 財務情報

株式数に関するカラム名は、文字数を短縮するため、および、意味を明確にするために、以下のように変更されます。

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

- J-Quants API では、調整済みの値に Adjustment プレフィックスを付けています。
  kabukit ではカラム名を単純化するために、プレフィックスのない Open, Close などで、調整済みの値を表します。
- Raw プレフィックスが付くカラムが、実際に取引に使われた、調整前の値です。

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

## EDINET API

EDINET API から返される lowerCamelCase または日本語のフィールド名は、
PascalCase に変更されます。
doc のような略語は、J-Quants API にあわせて、Document とします。
また、ユーザーが使用しないと考えらえるカラムは削除されます。

### 書類一覧

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
