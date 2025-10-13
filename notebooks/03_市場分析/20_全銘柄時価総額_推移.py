import marimo

__generated_with = "0.16.5"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md(
        """
    # 全銘柄 時価総額合計の推移分析

    株式市場全体の規模（価値の総和）が時系列でどのように変化してきたかを把握します。
    TOPIX（株価指数）の動きと、実際の市場全体の価値の動きを比較します。
    """
    )
    return


@app.cell
def _():
    import altair as alt
    import polars as pl

    from kabukit import Prices, Statements
    from kabukit.jquants.client import JQuantsClient
    return JQuantsClient, Prices, Statements, alt, pl


@app.cell
async def _(JQuantsClient, Prices, Statements):
    # 各種データを読み込む
    prices_raw = Prices()
    statements = Statements()
    async with JQuantsClient() as client:
        topix_df = await client.get_topix()
    return prices_raw, statements, topix_df


@app.cell
def _(pl, prices_raw, statements):
    # 全銘柄の日次時価総額を計算し、日付ごとに合計する
    total_market_cap_df = (
        prices_raw.with_adjusted_shares(statements)
        .with_market_cap()
        .data.filter(pl.col("MarketCap").is_not_null())
        .group_by("Date")
        .agg(pl.sum("MarketCap").alias("Value"))
        .sort("Date")
        .select("Date", "Value")
    )
    return (total_market_cap_df,)


@app.cell
def _(alt, pl, topix_df, total_market_cap_df):
    # 比較のために、TOPIXと時価総額合計を正規化（初日を100とする）して結合する

    # 1. それぞれのデータにカテゴリを追加
    df1 = total_market_cap_df.with_columns(pl.lit("時価総額合計").alias("Category"))
    df2 = topix_df.select(
        pl.col("Date"),
        pl.col("Close").alias("Value"),
        pl.lit("TOPIX").alias("Category"),
    )

    # 2. 2つのDataFrameを結合
    combined_df = pl.concat([df1, df2])

    # 3. カテゴリごとに正規化
    normalized_df = combined_df.with_columns(
        (100 * pl.col("Value") / pl.last("Value")).over("Category").alias("NormalizedValue")
    )

    # 4. チャートを作成
    chart = (
        alt.Chart(normalized_df, title="時価総額合計 vs TOPIX (期間初日=100)")
        .mark_line()
        .encode(
            x=alt.X("Date:T", title="日付"),
            y=alt.Y("NormalizedValue:Q", title="正規化後指数"),
            color=alt.Color("Category:N", title="指標"),
            tooltip=["Date", "Category", "Value"],
        )
    )
    return (chart,)


@app.cell
def _(chart):
    chart
    return


@app.cell
def _(total_market_cap_df):
    total_market_cap_df
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
