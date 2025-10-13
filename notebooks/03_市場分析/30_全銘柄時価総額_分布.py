import marimo

__generated_with = "0.16.5"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
    # 全銘柄 時価総額の分布分析

    最新時点での市場の構造を把握します。特に、どのような規模の企業（大型株、中型株、小型株）が
    どれくらいの数存在するのかを理解するために、時価総額の分布を可視化します。
    """
    )
    return


@app.cell
def _():
    import altair as alt
    import polars as pl

    from kabukit import Prices, Statements
    return Prices, Statements, alt, pl


@app.cell
def _(Prices, Statements, pl):
    # データを読み込み、最新日付の時価総額を計算
    prices_raw = Prices()
    statements = Statements()

    latest_market_cap_df = (
        prices_raw.with_adjusted_shares(statements)
        .with_market_cap()
        .data.filter(pl.col("Date") == pl.max("Date"))
        .filter(pl.col("MarketCap").is_not_null())
        .with_columns((pl.col("MarketCap") / 100_000_000).alias("MarketCap_Okuyen"))  # 億円単位に変換
    )
    return (latest_market_cap_df,)


@app.cell
def _(alt, latest_market_cap_df, pl):
    from scipy.stats import norm

    # 正規確率プロット用のデータを計算
    # 1. ランクと累積確率を計算 (polarsの新しいAPIを使用)
    # 2. 累積確率に対応するZ-scoreを計算
    prob_df = (
        latest_market_cap_df.sort("MarketCap_Okuyen")
        .with_row_index(name="rank")
        .with_columns(((pl.col("rank") + 1 - 0.5) / (pl.len())).alias("prob"))
        .with_columns(pl.col("prob").map_batches(norm.ppf).alias("z_score"))
    )

    # 3. 軸にグリッド線を表示するためのZ-scoreを定義
    tick_probs = [0.001, 0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99, 0.999]
    tick_z_scores = [norm.ppf(p) for p in tick_probs]

    # 4. 正規確率プロットを作成
    chart_prob = (
        alt.Chart(prob_df, title="時価総額の正規確率プロット")
        .mark_point(opacity=0.5, size=10)
        .encode(
            x=alt.X(
                "MarketCap_Okuyen:Q",
                title="時価総額（億円）",
                scale=alt.Scale(type="log"),
            ),
            y=alt.Y(
                "z_score:Q",
                title="Z-score (累積確率)",
            ),
            tooltip=[
                alt.Tooltip("Code"),
                alt.Tooltip("MarketCap_Okuyen", format=",.0f"),
                alt.Tooltip("prob", format=".2%", title="累積確率"),
            ],
        )
    )
    return (chart_prob,)


@app.cell
def _(chart_prob):
    chart_prob
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
