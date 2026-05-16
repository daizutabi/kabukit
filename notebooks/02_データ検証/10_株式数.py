import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")

with app.setup:
    from datetime import date

    import marimo as mo
    import polars as pl
    from polars import col as c

    from kabukit import Prices, Statements, Info


@app.cell(hide_code=True)
def _():
    mo.md("""
    # J-Quantsで取得できる財務情報を検証する
    """)
    return


@app.cell
def _():
    Info().data.filter(c.Code == "62000")
    return


@app.cell
def _():
    statements = Statements()
    prices = Prices().with_adjusted_shares(statements)
    return (prices,)


@app.cell
def _(prices):
    prices.data.filter(c.Code == "39970").select(
        "Date",
        "Close",
        "RawClose",
        "AdjustmentFactor",
        "AdjustedIssuedShares",
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
