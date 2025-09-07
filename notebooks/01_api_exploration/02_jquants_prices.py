import marimo

__generated_with = "0.15.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
    # 株価四本値 (`/prices/daily_quotes`)

    <https://jpx.gitbook.io/j-quants-ja/api-reference/daily_quotes>
    """
    )
    return


@app.cell
def _():
    import marimo as mo
    from polars import col as c
    from kabukit import JQuantsClient
    return JQuantsClient, mo


@app.cell
def _(JQuantsClient):
    client = JQuantsClient()
    return (client,)


@app.cell
async def _(client):
    await client.get_prices()
    return


@app.cell
async def _(client):
    await client.get_prices(code="1301")
    return


@app.cell
async def _(client):
    info = await client.get_info()
    codes = info["Code"]
    return (codes,)


@app.cell
async def _(client, codes):
    await client.get_prices(codes[1])
    return


@app.cell
def _():
    from kabukit.concurrent import fetch
    return (fetch,)


@app.cell
async def _(client, codes, fetch):
    df = await fetch(client.get_statements, codes[:3])
    df
    return (df,)


@app.cell
def _(df):
    df["DisclosedDate"]
    return


@app.cell
def _():
    import polars as pl

    pl.read_parquet("data/statements")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
