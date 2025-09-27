import marimo

__generated_with = "0.16.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # ファンダメンタル投資の教科書

    P014 図表0-2
    """
    )
    return


@app.cell
def _():
    import datetime
    import marimo as mo
    import polars as pl
    from polars import col as c
    from kabukit import JQuantsClient
    from kabukit.jquants.schema import rename
    from kabukit.utils.concurrent import concat
    from polars import DataFrame
    return DataFrame, JQuantsClient, c, concat, datetime, mo, rename


@app.cell
def _(JQuantsClient):
    client = JQuantsClient()
    return (client,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## 成長株の例: ビジョン (9416)""")
    return


@app.cell
async def _(c, client, rename):
    (await client.get_statements(code="9416")).filter(
        c.TypeOfDocument.str.contains("FYFinancialStatements"),
    ).select(
        c.Code,
        c.CurrentFiscalYearEndDate,
        c.NetSales / 1e6,
        c.OrdinaryProfit / 1e6,
        c.Profit / 1e6,
    ).pipe(rename).head(5)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## 割安株の例""")
    return


@app.cell
def _(DataFrame, JQuantsClient, c, datetime):
    async def get_price_ratio(code: list, date: datetime.date, column: str, name: str) -> DataFrame:
        async with JQuantsClient() as client:
            info = await client.get_info(code, date=date)
            price = await client.get_prices(code, date=date)
            stmt = await client.get_statements(code)

        info = info.select(c.CompanyName, c.Code)
        price = price.select(c.Code, c.Close)
        stmt = (
            stmt.filter(
                c.Date <= date,
                c(column).is_not_null(),
            )
            .select("Code", c(column))
            .tail(1)
        )
        return (
            info.join(price, on="Code")
            .join(stmt, on="Code", how="left")
            .with_columns((c.Close / c(column)).round(2).alias(name))
        )
    return (get_price_ratio,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### 低PER銘柄""")
    return


@app.cell
async def _(concat, datetime, get_price_ratio, rename):
    _aits = (
        get_price_ratio(code, datetime.date(2018, 9, 14), "ForecastEarningsPerShare", "PER")
        for code in ["1808", "4183", "8001"]
    )
    _df = await concat(_aits)
    _df.sort("Code").pipe(rename)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### 低PBR銘柄""")
    return


@app.cell
async def _(concat, datetime, get_price_ratio, rename):
    _aits = (
        get_price_ratio(code, datetime.date(2018, 9, 14), "BookValuePerShare", "PBR") for code in ["7494", "6178", "7911"]
    )
    _df = await concat(_aits)
    _df.sort("Code").pipe(rename)
    return


if __name__ == "__main__":
    app.run()
