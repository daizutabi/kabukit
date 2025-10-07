import marimo

__generated_with = "0.16.5"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
    # 上場銘柄一覧 (`/listed/info`)

    <https://jpx.gitbook.io/j-quants-ja/api-reference/listed_info>
    """,
    )
    return


@app.cell
def _():
    import marimo as mo
    import polars as pl
    from kabukit import JQuantsClient
    from kabukit.jquants import rename
    return JQuantsClient, mo, pl, rename


@app.cell
async def _(JQuantsClient, rename):
    async with JQuantsClient() as client:
        df = await client.get_info()
    rename(df)
    return (df,)


@app.cell
def _(df, pl):
    df["CompanyName"].value_counts().filter(pl.col("count") > 1).join(df, on="CompanyName")
    return


@app.cell
def _(df, pl):
    df.filter(pl.col("CompanyName").str.contains("優先株式"))
    return


@app.cell
async def _(JQuantsClient):
    async with JQuantsClient() as _client:
        _df = await _client.get_info("9434")
    _df
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
