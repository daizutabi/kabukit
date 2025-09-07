import marimo

__generated_with = "0.15.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
    # 上場銘柄一覧 (`/listed/info`)

    <https://jpx.gitbook.io/j-quants-ja/api-reference/listed_info>
    """
    )
    return


@app.cell
def _():
    import marimo as mo
    from polars import col as c
    from kabukit import JQuantsClient
    return JQuantsClient, c, mo


@app.cell
def _(JQuantsClient):
    client = JQuantsClient()
    return (client,)


@app.cell
async def _(c, client):
    df = await client.get_info()
    df = df.filter(c.Sector17CodeName != "その他", c.MarketCodeName != "TOKYO PRO MARKET")
    return (df,)


@app.cell
def _(df):
    df
    return


@app.cell
def _(df):
    df["Sector17CodeName"].unique()
    return


@app.cell
def _(df):
    df["Sector33CodeName"].unique()
    return


@app.cell
def _(df):
    df["MarketCodeName"].unique()
    return


@app.cell
async def _(client):
    await client.get_info(code="1301")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
