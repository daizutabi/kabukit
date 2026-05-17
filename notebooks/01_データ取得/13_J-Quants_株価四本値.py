import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo

    from kabukit import get_prices


@app.cell
async def _():
    await get_prices("3671")
    return


@app.cell
def _():
    button = mo.ui.run_button(label="複数銘柄の株価を取得する")
    button
    return (button,)


@app.cell
async def _(button):
    if button.value:
        await get_prices(max_items=30, progress=mo.status.progress_bar)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
