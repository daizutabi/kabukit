import marimo

__generated_with = "0.17.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    from kabukit import get_edinet_list
    return get_edinet_list, mo


@app.cell
async def _(get_edinet_list):
    await get_edinet_list("2025-10-31")
    return


@app.cell
def _(mo):
    button = mo.ui.run_button(label="全日付の書類一覧を取得する")
    button
    return (button,)


@app.cell
async def _(button, get_edinet_list, mo):
    if button.value:
        await get_edinet_list(years=1, progress=mo.status.progress_bar)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
