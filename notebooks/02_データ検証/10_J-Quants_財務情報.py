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


@app.cell
def _(c, data, pl):
    x=data.with_columns(c.TypeOfDocument.str.split("_").list.first()).group_by("TypeOfDocument").agg(
        pl.len(), pl.all().is_not_null().mean()
    ).sort("TypeOfDocument")
    return (x,)


@app.cell
def _(x):
    x.write_csv('a.csv')
    return


@app.cell
def _(data, pl):
    data.select(pl.col("^Result.*Annual.*$"))
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
