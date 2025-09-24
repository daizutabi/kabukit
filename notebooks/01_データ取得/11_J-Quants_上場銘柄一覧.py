import marimo

__generated_with = "0.16.0"
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
    import datetime

    import marimo as mo

    from kabukit import JQuantsClient, Info
    from kabukit.jquants.schema import InfoColumns
    return Info, InfoColumns, JQuantsClient, mo


@app.cell
def _(JQuantsClient):
    client = JQuantsClient()
    return (client,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    銘柄コードを与えると、指定した銘柄について情報を取得します。

    `InfoColumns.rename` 関数で、カラム名を日本語に変換できます。
    """,
    )
    return


@app.cell
async def _(InfoColumns, client):
    _df = await client.get_info("1301")
    InfoColumns.rename(_df)
    return


@app.cell
def _(mo):
    button = mo.ui.run_button(label="全銘柄の情報を取得する")
    button
    return (button,)


@app.cell
async def _(Info, button, client):
    if button.value:
        df = await client.get_info()
        Info(df).write()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
