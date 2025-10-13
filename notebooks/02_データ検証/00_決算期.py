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
    from kabukit import Statements, JQuantsClient
    return Statements, c, mo, pl


@app.cell
def _(Statements):
    Statements().data
    return


@app.cell
def _(Statements, c, pl):
    Statements().data.filter(
        ~c.TypeOfDocument.str.contains("Financial")
        | (c.TypeOfDocument.str.slice(0, 2) == c.TypeOfCurrentPeriod),
        c.TypeOfCurrentPeriod.is_in(["1Q", "2Q", "3Q", "FY"]),
    ).with_columns(
        (c.CurrentPeriodEndDate - c.CurrentPeriodStartDate).dt.total_days().alias("CurrentPeriodDays")
    ).filter(
        pl.when(c.TypeOfCurrentPeriod == "1Q")
        .then((c.CurrentPeriodDays > 80) & (c.CurrentPeriodDays < 100))
        .when(c.TypeOfCurrentPeriod == "2Q")
        .then((c.CurrentPeriodDays > 170) & (c.CurrentPeriodDays < 190))
        .when(c.TypeOfCurrentPeriod == "3Q")
        .then((c.CurrentPeriodDays > 260) & (c.CurrentPeriodDays < 280))
        .when(c.TypeOfCurrentPeriod == "FY")
        .then((c.CurrentPeriodDays > 350) & (c.CurrentPeriodDays < 380)),
        c.CurrentPeriodStartDate >= c.CurrentFiscalYearStartDate,
        c.CurrentPeriodEndDate <= c.CurrentFiscalYearEndDate,
    ).drop("CurrentPeriodDays")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
