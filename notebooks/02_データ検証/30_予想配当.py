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
    return Prices, Statements, c, mo, pl


@app.cell
def _(Prices, Statements):
    statements = Statements.read()
    prices = Prices.read()
    return prices, statements


@app.cell
def _(c, pl, prices, statements):
    prices.with_adjusted_shares(statements).with_forecast_dividend(statements).filter(
        c.Code == "39970"
        # c.Code == "72030"
    ).data.select(
        "Date",
        pl.col("RawClose"),
        "AdjustedIssuedShares",
        "ForecastDividend",
        (c.ForecastDividend / (c.AdjustedIssuedShares - c.AdjustedTreasuryShares)).round(2).alias("DPS"),
        (c.RawClose * (c.AdjustedIssuedShares - c.AdjustedTreasuryShares*0)).alias("時価総額"),
    ).with_columns((c.DPS / c.RawClose * 100).alias("配当利回り"))
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
