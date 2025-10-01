import marimo

__generated_with = "0.16.3"
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
    return Prices, Statements, c, date, mo


@app.cell
def _(Prices, Statements):
    statements = Statements.read()
    prices = Prices.read()
    return (statements,)


@app.cell
def _(c, date, statements):
    statements.number_of_shares().filter(c.Code == "39970", c.Date > date(2025, 1, 1))
    return


@app.cell
def _(statements):
    statements.data.filter(Code="39970")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
