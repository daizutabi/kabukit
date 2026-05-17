import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo

    from kabukit import JQuantsClient
    from kabukit.analysis.visualization import plot_topix_timeseries


@app.cell
async def _():
    async with JQuantsClient() as client:
        topix_df = await client.get_topix()
    return (topix_df,)


@app.cell
def _(topix_df):
    # チャートの描画
    chart = plot_topix_timeseries(topix_df).properties(width="container")
    mo.ui.altair_chart(chart)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
