# 株価指標の計算方針

## 概要

時系列分析（バックテストなど）で収益利回りなどの株価指標を計算する際の、統一的な計算方針を定める。特に、株式分割や増資などで発行済株式数が変動する場合の取り扱いを明確にすることを目的とする。

## 基本原則

過去のある時点 `t` における指標を計算する場合、その時点 `t` で投資家が入手可能だった情報のみを利用する。これにより、将来のデータを利用してしまう「ルックアヘッド・バイアス」を完全に排除する。

## 共通の計算前提

各株価指標を計算する上で共通となる前提と、日次で調整されるデータの算出方法を定義する。

1. **株価の取得**:
   * 計算対象日 `t` の**調整されていない、生の株価** (`RawClose`) を取得する。

2. **財務諸表の特定**:
   * 計算対象日 `t` までに公表された、**最も新しい決算情報**（決算短信など）を特定する。

3. **基準となる財務情報の取得**:
   * 特定した決算情報から、以下の基準値を取得する。
     * `IssuedShares` (発行済株式数)
     * `TreasuryShares` (自己株式数)
     * `Equity` (純資産)
     * `ForecastProfit` (当期予想純利益, FY決算以外)
     * `NextYearForecastProfit` (来期予想純利益, FY決算)
     * `ForecastDividendPerShareAnnual` (当期予想配当, FY決算以外)
     * `NextYearForecastDividendPerShareAnnual` (来期予想配当, FY決算)

4. **株式数の更新と流通株式数の算出**:
   * `daily_adjusted_shares.md` に記載されているロジックに基づき、日々の株価データに含まれる `AdjustmentFactor` を用いて、`IssuedShares` (発行済株式数) と `TreasuryShares` (自己株式数) を日次で調整する。
   * これにより、各日 `t` における `AdjustedIssuedShares` (調整後発行済株式数) と `AdjustedTreasuryShares` (調整後自己株式数) を算出する。
   * `流通株式数` = `AdjustedIssuedShares` - `AdjustedTreasuryShares` の計算式で、当日 `t` 時点での有効な流通株式数を求める。この処理は、過去の基準値を現在の状態に合わせる「**更新**」と位置づける。

## 各指標の計算アルゴリズム

上記「共通の計算前提」で算出されたデータを用いて、各株価指標を計算する。

### 純資産利回り (Book-value Yield)

企業の資産価値に対する株価の割安度を測る指標。PBRの逆数に相当する。

```text
純資産利回り = Equity / (流通株式数 × RawClose)
```

### 収益利回り (Earnings Yield)

企業の利益創出力を測る指標。PERの逆数に相当する。収益は予想を用いる。
（注: ここでいう「収益」は「純利益」を指す。）

```text
収益利回り = 予想純利益 / (流通株式数 × RawClose)
```

ここで、`予想純利益`は、以下の条件に基づき決定する。

* 最新の決算情報がFY決算のとき、`NextYearForecastProfit` (来期の予想純利益) を使用する。
* 最新の決算情報がFY決決算以外 (1Q, 2Q, 3Q) のとき、`ForecastProfit` (当期の予想純利益) を使用する。

### 配当利回り (Dividend Yield)

株主への直接還元を測る指標。配当は予想を用いる。

```text
配当利回り = 予想年間配当総額 / (流通株式数 × RawClose)
```

ここで、`予想年間配当総額`は、以下の条件に基づき決定する。

* 最新の決算情報がFY決算のとき、

    `予想年間配当総額 = NextYearForecastDividendPerShareAnnual × (NextYearForecastProfit / NextYearForecastEarningsPerShare)`
* 最新の決算情報がFY決決算以外 (1Q, 2Q, 3Q) のとき、

    `予想年間配当総額 = ForecastDividendPerShareAnnual × (ForecastProfit / ForecastEarningsPerShare)`

(注1) `ForecastTotalDividendPaidAnnual` および `NextYearForecastTotalDividendAnnual` はデータが欠落しているか、カラム自体が存在しない。

(注2) 予想の期間中に株式分割などにより株式数が変化することが見込まれるとき、「一株あたり」の算出に用いられる株式数は`AverageOutstandingShares`に一致しない。また、そのような株式数は決算データからは得られない。そのため、予想DPSと予想EPSの算出に用いられる株式数が一致するとの仮定に基づき、上式で計算する。

## このアプローチの利点

* **企業行動の反映**: 新しい決算が公表されると、`IssuedShares` (発行済株式数) や `TreasuryShares` (自己株式数) が更新されるため、増資、自己株式取得、株式償却などの企業行動が自然に反映される。
* **株式分割・併合の反映**: `AdjustmentFactor` を用いた日次調整により、株価と株式数の間の不整合を解消し、過去に遡って正確な流通株式数を維持する。
* **直感的な分かりやすさ**: すべての利回り指標が「高いほど良い（割安・高効率）」という統一された基準で評価可能となり、計算の意図が明確になる。
* **将来情報の排除**: 計算の各ステップで、その時点で入手不可能な将来のデータ（未来の決算、未来から見た調整後株価など）を利用しない。
