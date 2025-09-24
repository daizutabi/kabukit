import marimo

__generated_with = "0.16.1"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
    # 財務情報 (`/fins/statements`)

    四半期の財務情報が取得できます。

    <https://jpx.gitbook.io/j-quants-ja/api-reference/statements>
    """,
    )
    return


@app.cell
def _():
    import datetime

    import marimo as mo

    from kabukit import JQuantsClient, Statements
    from kabukit.jquants import fetch_all
    return JQuantsClient, Statements, fetch_all, mo


@app.cell
def _(JQuantsClient):
    client = JQuantsClient()
    return (client,)


@app.cell
async def _(client):
    await client.get_statements(date="20250901")
    return


@app.cell
async def _(client):
    import polars as pl
    (await client.get_statements(date="20250901")).select(pl.col("^.*NumberOf.*$"))
    return


@app.cell
def _(mo):
    button = mo.ui.run_button(label="全銘柄の財務情報を取得する")
    button
    return (button,)


@app.cell
async def _(Statements, button, fetch_all, mo):
    if button.value:
        df = await fetch_all("statements", progress=mo.status.progress_bar)
        Statements(df).write()
    return


if __name__ == "__main__":
    app.run()
