import marimo

__generated_with = "0.16.5"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
    # 株価四本値 (`/prices/daily_quotes`)

    <https://jpx.gitbook.io/j-quants-ja/api-reference/daily_quotes>
    """,
    )


@app.cell
def _():
    import marimo as mo

    from kabukit import JQuantsClient, get_prices

    return JQuantsClient, get_prices, mo


@app.cell
async def _(JQuantsClient):
    async with JQuantsClient() as client:
        df = await client.get_prices("3671")
    df


@app.cell
def _(mo):
    button = mo.ui.run_button(label="全銘柄の株価を取得する")
    button
    return (button,)


@app.cell
async def _(button, get_prices, mo):
    if button.value:
        await get_prices(max_items=30, progress=mo.status.progress_bar)


if __name__ == "__main__":
    app.run()
