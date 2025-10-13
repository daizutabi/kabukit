import marimo

__generated_with = "0.16.5"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    from kabukit import EdinetClient, get_entries
    return EdinetClient, get_entries, mo


@app.cell
async def _(EdinetClient):
    async with EdinetClient() as client:
        df = await client.get_entries("2025-09-22")
    df
    return


@app.cell
def _(mo):
    button = mo.ui.run_button(label="全日付の書類一覧を取得する")
    button
    return (button,)


@app.cell
async def _(button, get_entries, mo):
    if button.value:
        await get_entries(years=1, progress=mo.status.progress_bar)
    return


if __name__ == "__main__":
    app.run()
