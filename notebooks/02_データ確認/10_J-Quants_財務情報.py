import marimo

__generated_with = "0.16.1"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
    # J-Quantsで取得できる財務情報を確認する

    <https://jpx.gitbook.io/j-quants-ja/api-reference/statements>
    """
    )
    return


@app.cell
def _():
    import marimo as mo
    import polars as pl
    from polars import col as c
    from kabukit import Statements
    return Statements, c, mo


@app.cell
def _(Statements):
    data = Statements.read().data
    data.shape
    return (data,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## TypeOfDocument: 開示書類種別

    - FinancialStatements: 決算短信
    - DividendForecastRevision: 配当予想の修正
    - EarnForecastRevision: 業績予想の修正
    """
    )
    return


@app.cell
def _(data):
    data["TypeOfDocument"].unique().sort()
    return


@app.cell
def _(c, data):
    data.filter(c.TypeOfDocument.str.contains("Financial"))["TypeOfDocument"].str.split("_").list.first().unique().sort()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## 各書類で有効なカラム""")
    return


@app.cell
def _(data):
    data.filter(Code="33500").select(
        "Date", "Code", "TypeOfDocument", "TotalAssets", "Equity", "BookValuePerShare", "^.*NumberOf.*$"
    )
    return


@app.cell
def _():
    16965000000/36268334
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## 決算短信""")
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
