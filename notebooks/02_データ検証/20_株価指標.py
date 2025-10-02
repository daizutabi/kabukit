import marimo

__generated_with = "0.16.4"
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
    return Statements, c, date, mo


@app.cell
def _(Statements, c, date):
    x = (
        Statements.read()
        .filter(c.Code == "39970", c.DisclosedDate == date(2025, 8, 8))
        .data.row(0, named=True)
    )
    return (x,)


@app.cell
def _(x):
    x["Profit"]
    return


@app.cell
def _(x):
    x["EarningsPerShare"]
    return


@app.cell
def _(x):
    x["AverageOutstandingShares"]
    return


@app.cell
def _():
    actual_profit = -69_558_000
    return (actual_profit,)


@app.cell
def _(actual_profit, x):
    round(actual_profit / x["AverageOutstandingShares"], 2)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
