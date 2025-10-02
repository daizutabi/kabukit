import marimo

__generated_with = "0.16.4"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md("""# J-Quantsで取得できる財務情報を検証する""")
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
    prices = Prices.read().with_adjusted_shares(statements)
    return (prices,)


@app.cell
def _(c, prices):
    prices.data.filter(c.Code == "62000").select(
        "Date", "Close","RawClose", "AdjustmentFactor", "AdjustedTotalShares"
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
