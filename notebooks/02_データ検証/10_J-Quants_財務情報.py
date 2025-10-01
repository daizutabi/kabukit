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
    return Prices, Statements, c, date, mo, pl


@app.cell
def _(Prices, Statements):
    statements = Statements.read()
    prices = Prices.read()
    return prices, statements


@app.cell
def _(c, date, statements):
    statement_df = (
        statements.number_of_shares()
        .filter(c.Code == "39970", c.Date > date(2025, 1, 1))
        .select("Date", "Code", Shares=c.TotalShares - c.TreasuryShares)
    )
    statement_df
    return (statement_df,)


@app.cell
def _(c, date, prices):
    prices_df = prices.data.filter(c.Code == "39970", c.Date > date(2025, 1, 1)).select(
        "Date", "Code", "AdjustmentFactor", "Volume", "RawVolume"
    )
    prices_df.tail()
    return (prices_df,)


@app.cell
def _(c, prices_df):
    prices_df.filter(c.AdjustmentFactor != 1)
    return


@app.cell
def _(prices_df, statement_df):
    daily_df = prices_df.join_asof(
        statement_df.rename({"Date": "ReportDate", "Shares": "ReportedShares"}),
        left_on="Date",
        right_on="ReportDate",
        by="Code",
        check_sortedness=False,
    )
    daily_df.tail()
    return (daily_df,)


@app.cell
def _(c, daily_df, pl):
    adjusted_df = daily_df.with_columns(
        (1.0 / c.AdjustmentFactor).cum_prod().over("Code", "ReportDate").alias("CumulativeRatio")
    ).with_columns((c.ReportedShares * c.CumulativeRatio).round(0).cast(pl.Int64))
    adjusted_df
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
