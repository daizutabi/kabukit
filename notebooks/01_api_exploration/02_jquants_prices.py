import marimo

__generated_with = "0.15.3"
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
    import polars as pl
    from polars import col as c
    from kabukit import JQuantsClient
    from kabukit.concurrent import collect_fn
    return JQuantsClient, collect_fn, mo, pl


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
    await client.get_prices("1301")
    return


@app.cell
async def _(client, collect_fn, pl):
    pl.concat([df async for df in collect_fn(client.get_prices, ["1301", "1332"]) if not df.is_empty()])
    return


if __name__ == "__main__":
    app.run()
