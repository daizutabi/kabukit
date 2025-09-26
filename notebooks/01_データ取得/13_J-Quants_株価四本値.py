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
    from kabukit.jquants import fetch_all, rename
    return JQuantsClient, fetch_all, mo, rename


@app.cell
async def _(JQuantsClient, rename):
    async with JQuantsClient() as client:
        df = await client.get_prices("3671")
    rename(df)
    return


@app.cell
def _(mo):
    button = mo.ui.run_button(label="全銘柄の株価を取得する")
    button
    return (button,)


@app.cell
async def _(button, fetch_all, mo):
    if button.value:
        await fetch_all("prices", limit=30, max_concurrency=8, progress=mo.status.progress_bar)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
