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
    from kabukit import Statements
    return Statements, c, mo, pl


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
    mo.md(
        r"""
    ## 各書類で有効なカラム

    ### すべての書類でnullを含まないカラム
    """
    )
    return


@app.cell
def _(data):
    common_columns = [s.name for s in data if s.is_not_null().all() and s.name != "TypeOfDocument"]
    common_columns
    return (common_columns,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### 真偽値カラム""")
    return


@app.cell
def _(data, pl):
    bool_columns = [s.name for s in data if s.dtype == pl.Boolean]
    bool_columns
    return (bool_columns,)


@app.cell
def _(bool_columns, common_columns, data, pl):
    pct = (
        data.drop(common_columns, bool_columns)
        .group_by("TypeOfDocument")
        .agg(pl.len(), pl.exclude(common_columns, "Time").is_not_null().sum())
        .with_columns((pl.exclude("TypeOfDocument", "len") / pl.col("len") * 100).round(1))
        .sort("TypeOfDocument")
    )
    pct
    return (pct,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### 決算短信""")
    return


@app.cell
def _(c, pct):
    _df = pct.filter(c.TypeOfDocument.str.contains("1QFinancial"))
    _df.select(s.name for s in _df if s.name == "TypeOfDocument" or s.max() > 0)
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
