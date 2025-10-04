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
def _(c, prices, statements):
    prices.with_adjusted_shares(statements).with_forecast_profit(statements).filter(
        # c.Code == "39970"
        c.Code == "72030"
    ).data.select(
        "Date",
        "RawClose",
        "AdjustedIssuedShares",
        "ForecastProfit",
        (c.ForecastProfit / (c.AdjustedIssuedShares - c.AdjustedTreasuryShares)).round(2).alias("EPS"),
    ).with_columns((c.RawClose / c.EPS).round(2).alias("PER"))
    return


@app.cell
def _(c, prices, statements):
    prices.with_adjusted_shares(statements).with_forecast_profit(
        statements
    ).with_earnings_yield().filter(
        c.Code == "39970"
        # c.Code == "72030"
    ).data.select(
        "Date",
        "RawClose",
        "AdjustedIssuedShares",
        "ForecastProfit",
        "EarningsPerShare",
        "EarningsYield",
    )
    return


@app.cell
def _():
    1/0.0093
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
