import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo

    from kabukit import get_jpx_shares


@app.cell
async def _():
    await get_jpx_shares(max_items=3)
    return


@app.cell
def _():
    button = mo.ui.run_button(label="全日付の書類一覧を取得する")
    button
    return (button,)


@app.cell
async def _(button):
    if button.value:
        await get_jpx_shares(progress=mo.status.progress_bar)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
