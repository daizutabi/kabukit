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
    import datetime
    import marimo as mo
    from kabukit import JQuantsClient
    return JQuantsClient, datetime, mo


@app.cell
def _(JQuantsClient):
    client = JQuantsClient.create()
    return (client,)


@app.cell
async def _(client, datetime):
    info = await client.get_info(date=datetime.date.today())
    return (info,)


@app.cell
def _(info):
    info.columns
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
