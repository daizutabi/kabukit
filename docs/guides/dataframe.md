# DataFrame

kabukit が返す DataFrame のカラム名は、データソース（J-Quants, EDINETなど）によらず、
一貫した命名規則に従うよう設計されています。
J-Quants API の仕様にならって、全てのカラム名は PascalCase で記述されます。
これにより、利用者はソースの違いを意識することなく、統一された使いやすいインターフェースでデータを扱うことができます。

## J-Quants API

J-Quants API から返される JSON データを DataFrame に変換する際、
後続の分析を行いやすくするために、一部のカラム名が変更されます。

### 上場銘柄一覧

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

- J-Quants API では、調整済みの値に `Adjustment` プレフィックスを付けています。
  kabukit ではカラム名を単純化するために、プレフィックスのない `Open`, `Close` などで、調整済みの値を表します。
- `Raw` プレフィックスが付いているものが、調整前の実際に取引に使われた値です。

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

J-Quants API には DisclosedDate および DisclosedTime フィールドが存在します。
また、TDnet でも、ウェブページから DisclosedDate および DisclosedTime を簡単に
決定できます。
このため、15:30 を市場の取引時間後の閾値（スレッショルド）として Date を計算するロジックは比較的単純です。

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
