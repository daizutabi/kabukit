import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")

with app.setup:
    import polars as pl
    from polars import col as c

    from kabukit import Statements


@app.cell
def _():
    Statements().data
    return


@app.cell
def _():
    Statements().data.filter(
        ~c.TypeOfDocument.str.contains("Financial")
        | (c.TypeOfDocument.str.slice(0, 2) == c.TypeOfCurrentPeriod),
        c.TypeOfCurrentPeriod.is_in(["1Q", "2Q", "3Q", "FY"]),
    ).with_columns(
        (c.CurrentPeriodEndDate - c.CurrentPeriodStartDate)
        .dt.total_days()
        .alias("CurrentPeriodDays"),
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


if __name__ == "__main__":
    app.run()
