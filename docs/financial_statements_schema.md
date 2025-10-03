# Financial Statements Schema

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

- 実績値では以下が成り立つ
  - ResultTotalDividendPaidAnnual = ResultDividendPerShareAnnual * AverageOutstandingShares
- 予想値では、データが欠落しているので、同様にして、
  - ForecastTotalDividendPaidAnnual = ForecastDividendPerShareAnnual * AverageOutstandingShares
  - NextYearForecastTotalDividendPaidAnnual = NextYearForecastDividendPerShareAnnual * AverageOutstandingShares
  で計算する。