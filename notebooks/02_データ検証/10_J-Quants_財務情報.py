import marimo

__generated_with = "0.16.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md("""# J-Quantsで取得できる財務情報を検証する""")
    return


@app.cell
def _():
    import marimo as mo
    import polars as pl
    from polars import col as c
    from kabukit import Statements, Prices
    return Prices, Statements, mo


@app.cell
def _(Prices, Statements):
    statements = Statements.read()
    prices = Prices.read()
    return (statements,)


@app.cell
def _(statements):
    statements.number_of_shares().filter(Code="39970")
    return


@app.cell
def _():
    (3901800+920)*10
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
