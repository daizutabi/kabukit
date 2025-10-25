import marimo

__generated_with = "0.17.2"
app = marimo.App(width="medium", sql_output="polars")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    from kabukit import EdinetClient, get_edinet_documents, EdinetList
    return EdinetClient, EdinetList, mo, pl


@app.cell
async def _(EdinetClient):
    async with EdinetClient() as client:
        df = await client.get_document("S100WQ4C")
    df
    return


@app.cell
def _(mo):
    button = mo.ui.run_button(label="全銘柄の報告書を取得する")
    button
    return (button,)


@app.cell
async def _(EdinetList, button, get_documents, mo, pl):
    if button.value:
        lst = EdinetList().data.filter(pl.col("Code").is_not_null(), pl.col("CsvFlag"))
        doc_ids = lst["docID"].unique()
        x = await get_documents(doc_ids, max_items=100, progress=mo.status.progress_bar)
        mo.output.append(x)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
