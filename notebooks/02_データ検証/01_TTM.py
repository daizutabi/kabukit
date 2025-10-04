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
    return JQuantsClient, Statements, c, date, mo, pl


@app.cell
def _(Statements, c):
    data = (
        Statements.read()
        .data.with_columns(
            (c.CurrentPeriodEndDate - c.CurrentPeriodStartDate)
            .dt.total_days()
            .alias("CurrentPeriodDays")
        )
        .select(
            "Date",
            "Code",
            "TypeOfDocument",
            "TypeOfCurrentPeriod",
            "CurrentPeriodDays",
            c.TypeOfDocument.str.slice(0, 2).alias("a"),
        )
        .filter(
            c.TypeOfDocument.str.contains("Financial"),
            ~c.TypeOfDocument.str.contains("Other"),
            c.TypeOfDocument.str.slice(0, 2) != c.TypeOfCurrentPeriod,
        )
    )
    return (data,)


@app.cell
def _(data):
    data
    return


@app.cell
def _(Statements, c, pl):
    x = (
        Statements.read()
        .data.filter(
            c.TypeOfDocument.str.contains("^(1Q|2Q|3Q|FY)Financial.*$"),
        )
        .with_columns(c.TypeOfDocument.str.slice(0, 2).alias("Q"))
        .with_columns(c.Q.shift().over("Code").alias("PQ"))
        .filter(c.PQ.is_not_null())
        .with_columns(pl.concat_str([c.PQ, c.Q], separator="-").alias("PQ_Q"))
    )
    x.group_by("PQ_Q").agg(pl.len())
    return (x,)


@app.cell
def _(c, x):
    x.filter(c.PQ_Q == "1Q-3Q")
    return


@app.cell
def _(Statements, c):
    Statements.read().data.filter(c.Code == "17950")
    return


@app.cell
async def _(JQuantsClient):
    async with JQuantsClient() as client:
        df = await client.get_statements("17950", with_date=False)
    df
    return (df,)


@app.cell
def _(c, df):
    _x = df.filter(c.DisclosureNumber.is_in(["20180510433330", "20180115450784"]))

    _x.select(c for c in _x.columns if _x[c].n_unique() != 1)
    return


@app.cell
def _(df, pl):
    df.unique(
        pl.exclude("DisclosedDate", "DisclosedTime", "Code", "DisclosureNumber"),
        keep="first",
        maintain_order=True,
    )
    return


@app.cell
def _(c, date, df):
    df.filter(c.DisclosedDate == date(2018, 5, 10))
    return


@app.cell
def _(c, date, df):
    from kabukit.jquants.statements import unique

    unique(df).filter(c.DisclosedDate == date(2018, 5, 10))
    return (unique,)


@app.cell
def _(df, unique):
    unique(df)
    return


@app.cell
def _(c, df, unique):
    df.filter(~c.DisclosureNumber.is_in(unique(df)["DisclosureNumber"].to_list()))
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
