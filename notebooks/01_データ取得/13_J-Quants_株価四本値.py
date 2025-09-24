import marimo

__generated_with = "0.16.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
    # 株価四本値 (`/prices/daily_quotes`)

    <https://jpx.gitbook.io/j-quants-ja/api-reference/daily_quotes>
    """,
    )
    return


@app.cell
def _():
    import datetime
    from pathlib import Path

    import marimo as mo
    from polars import DataFrame

    from kabukit import JQuantsClient, Prices
    from kabukit.jquants.schema import PriceColumns
    from kabukit.jquants import fetch_all
    return JQuantsClient, PriceColumns, Prices, fetch_all, mo


@app.cell
def _(JQuantsClient):
    client = JQuantsClient()
    return (client,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    銘柄コードを与えると、指定した銘柄の全期間の株価を取得します。

    `PriceColumns.rename` 関数で、カラム名を日本語に変換できます。
    """,
    )
    return


@app.cell
async def _(PriceColumns, client):
    _df = await client.get_prices("3671")
    PriceColumns.rename(_df).head()
    return


@app.cell
def _(mo):
    button = mo.ui.run_button(label="全銘柄の株価を取得する")
    button
    return (button,)


@app.cell
async def _(Prices, button, fetch_all, mo):
    if button.value:
        df = await fetch_all("prices", max_concurrency=8, progress=mo.status.progress_bar)
        Prices(df).write()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
