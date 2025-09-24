import marimo

__generated_with = "0.16.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import datetime
    import marimo as mo
    import polars as pl
    import altair as alt
    from kabukit import JQuantsClient
    from polars import col as c
    return JQuantsClient, mo


@app.cell
def _(JQuantsClient):
    client = JQuantsClient()
    return (client,)


@app.cell
async def _(client):
    df = await client.get_prices("6200")
    df
    return (df,)


@app.cell
def _(df, mo):
    from kabukit.analysis.visualization import plot_prices
    from kabukit import Prices

    prices = Prices(df).truncate("1mo")
    chart = plot_prices(prices)

    mo.ui.altair_chart(chart)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
