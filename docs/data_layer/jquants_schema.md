# J-Quants 財務諸表スキーマ

## 一覧

```
                         損益計算書 貸借対照表 キャッシュフロー 株式数
1QFinancialStatements    o        o        o             o
2QFinancialStatements    o        o        o             o
3QFinancialStatements    o        o        o             o
FYFinancialStatements    o        o        o             o
OtherPeriodFinancialS    o        o        o

                         配当実績
                         ResultDividendPerShare
                         1st 2nd 3rd FYE        ResultXXXAnnual
1QFinancialStatements    o
2QFinancialStatements    o   o
3QFinancialStatements    o   o   o
FYFinancialStatements    o   o   o   o          o

                         損益予想 (当期)
                         ForecastXXX2ndQuarter ForecastXXX
1QFinancialStatements    o                     o
2QFinancialStatements                          o
3QFinancialStatements                          o
EarnForecastRevision     o                     o

                         損益予想 (来期)
                         NextYearForecastXXX2ndQuarter NextYearForecastXXX
FYFinancialStatements    o                             o

                         配当予想 (当期)
                         ForecastDividendPerShare
                         1st 2nd 3rd FYE          ForecastXXXAnnual
1QFinancialStatements        o   o   o            o
2QFinancialStatements            o   o            o
3QFinancialStatements                o            o
DividendForecastRevision o   o   o   o            o
EarnForecastRevision     o   o   o   o            o

                         配当予想 (来期)
                         NextYearForecastDividendPerShare
                         1st 2nd 3rd FYE                  NextYerForecastXXXAnnual
FYFinancialStatements    o   o   o   o                    o
```

## 配当予想 (当期)

- 通期決算以外で有効
- ForecastDividendPerShareAnnual: 有効
- ForecastTotalDividendPaidAnnual: すべてnull
- ForecastPayoutRatioAnnual: すべてnull

## 配当予想 (来期)

- 通期決算で有効
- NextYearForecastDividendPerShareAnnual: 有効
- NextYearForecastTotalDividendPaidAnnual: カラム自体が欠落
- NextYearForecastPayoutRatioAnnual: 有効

## 配当金総額の算出方法

J-Quants APIから直接取得できる `ForecastTotalDividendPaidAnnual` などの配当金総額の予想値は、データが欠落しているかカラム自体が存在しません。

そのため、`kabukit`では、他の予想値から配当金総額を算出します。

- **実績値**:
  - `ResultTotalDividendPaidAnnual` は `ResultDividendPerShareAnnual * AverageOutstandingShares` で検証可能です。
- **予想値**:
  - 予想1株あたり配当 (`ForecastDividendPerShareAnnual`) と、予想EPSの計算に使われた株式数（`ForecastProfit / ForecastEarningsPerShare` で逆算）を掛け合わせて算出します。
  - 詳細な計算ロジックと、その背景にある設計思想については、[株価指標の計算方針](indicator_calculation.md)を参照してください。
