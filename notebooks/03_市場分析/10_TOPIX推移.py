import marimo

__generated_with = "0.16.5"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md(
        """
    # TOPIXの時系列分析

    市場全体のパフォーマンスを示す代表的なベンチマークとして、TOPIXの動向を把握します。
    """
    )
    return


@app.cell
def _():
    from kabukit.analysis.visualization import plot_topix_timeseries
    from kabukit.jquants.client import JQuantsClient
    return JQuantsClient, plot_topix_timeseries


@app.cell
async def _(JQuantsClient):
    async with JQuantsClient() as client:
        topix_df = await client.get_topix()
    return (topix_df,)


@app.cell
def _(mo, plot_topix_timeseries, topix_df):
    # チャートの描画
    chart = plot_topix_timeseries(topix_df)
    mo.ui.altair_chart(chart)
    return


@app.cell
def _(topix_df):
    topix_df
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
