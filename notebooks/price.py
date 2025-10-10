import marimo

__generated_with = "0.16.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import datetime

    import altair as alt
    import marimo as mo
    import polars as pl
    from polars import col as c

    from kabukit import JQuantsClient
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
    from kabukit import Prices
    from kabukit.analysis.visualization import plot_prices

    prices = Prices(df).truncate("1mo")
    chart = plot_prices(prices)

    mo.ui.altair_chart(chart)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
