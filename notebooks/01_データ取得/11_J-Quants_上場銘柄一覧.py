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
    return JQuantsClient, mo


@app.cell
async def _(JQuantsClient):
    async with JQuantsClient() as client:
        df = await client.get_info()
    df
    return


if __name__ == "__main__":
    app.run()
