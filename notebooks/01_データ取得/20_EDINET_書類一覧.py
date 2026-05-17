import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo

    from kabukit import get_edinet_list


@app.cell
async def _():
    await get_edinet_list("2025-10-31")
    return


@app.cell
def _():
    button = mo.ui.run_button(label="1年分の書類一覧を取得する")
    button
    return (button,)


@app.cell
async def _(button):
    if button.value:
        await get_edinet_list(years=1, progress=mo.status.progress_bar)
    return


if __name__ == "__main__":
    app.run()
