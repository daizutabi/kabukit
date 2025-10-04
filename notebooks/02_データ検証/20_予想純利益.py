import marimo

__generated_with = "0.16.5"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
    # J-Quantsで取得できる財務情報を検証する

    <https://pdf.irpocket.com/C3997/bffO/ugVK/I9Yg.pdf>
    """
    )
    return


@app.cell
def _():
    import marimo as mo
    from datetime import date
    import polars as pl
    from polars import col as c
    from kabukit import Statements, Prices
    return Prices, Statements, c, mo


@app.cell
def _(Prices, Statements):
    statements = Statements.read()
    prices = Prices.read()
    return prices, statements


@app.cell
def _(c, statements):
    statements.data.filter(c.Code == "39970").select(
        "Date",
        "TypeOfDocument",
        "Profit",
        "EarningsPerShare",
        "AverageOutstandingShares",
        "ResultDividend"
        (c.EarningsPerShare * c.AverageOutstandingShares).alias("a"),
        "ForecastProfit",
        "ForecastEarningsPerShare",
        (c.ForecastProfit / c.ForecastEarningsPerShare).alias("b"),
    )
    return


@app.cell
def _(c, prices, statements):
    prices.with_forecast_profit(statements).data.filter(c.Code == "72030").select(
        "Date",
        "ForecastProfit",
    )
    return


if __name__ == "__main__":
    app.run()
