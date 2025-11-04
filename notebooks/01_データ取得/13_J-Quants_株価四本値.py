import marimo

__generated_with = "0.17.6"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # 株価四本値 (`/prices/daily_quotes`)

    <https://jpx.gitbook.io/j-quants-ja/api-reference/daily_quotes>
    """)
    return


@app.cell
def _():
    import marimo as mo

    from kabukit import get_prices
    return get_prices, mo


@app.cell
async def _(get_prices):
    await get_prices("3671")
    return


@app.cell
def _(mo):
    button = mo.ui.run_button(label="全銘柄の株価を取得する")
    button
    return (button,)


@app.cell
async def _(button, get_prices, mo):
    if button.value:
        await get_prices(max_items=30, progress=mo.status.progress_bar)
    return


if __name__ == "__main__":
    app.run()
