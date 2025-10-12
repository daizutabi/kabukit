import marimo

__generated_with = "0.16.5"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    from kabukit import EdinetClient
    from kabukit.edinet import fetch_documents
    return EdinetClient, fetch_documents, mo


@app.cell
async def _(EdinetClient):
    async with EdinetClient() as client:
        df = await client.get_documents("2025-09-22")
    df
    return


@app.cell
def _(mo):
    button = mo.ui.run_button(label="全日付の書類一覧を取得する")
    button
    return (button,)


@app.cell
async def _(button, fetch_documents, mo):
    if button.value:
        lst = await fetch_documents(years=10, progress=mo.status.progress_bar)
        mo.output.append(lst.sort("Date"))
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
