import marimo

__generated_with = "0.16.2"
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
    import marimo as mo
    from kabukit import JQuantsClient
    from kabukit.jquants.schema import rename
    return JQuantsClient, mo, rename


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    銘柄コードを与えると、指定した銘柄の全期間の株価を取得します。

    `rename` 関数で、カラム名を日本語に変換できます。
    """,
    )
    return


@app.cell
async def _(JQuantsClient, rename):
    async with JQuantsClient() as client:
        df = await client.get_prices("3671")
    rename(df)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
