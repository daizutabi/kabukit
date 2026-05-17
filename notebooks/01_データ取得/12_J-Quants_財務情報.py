import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo

    from kabukit import get_statements


@app.cell
async def _():
    await get_statements("1301")
    return


@app.cell
def _():
    button = mo.ui.run_button(label="複数銘柄の財務情報を取得する")
    button
    return (button,)


@app.cell
async def _(button):
    if button.value:
        await get_statements(max_items=100, progress=mo.status.progress_bar)
    return


if __name__ == "__main__":
    app.run()
