import marimo

__generated_with = "0.16.2"
app = marimo.App(width="medium", sql_output="polars")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    from kabukit import List, EdinetClient
    from kabukit.edinet import fetch_csv
    return EdinetClient, List, fetch_csv, mo, pl


@app.cell
async def _(EdinetClient):
    async with EdinetClient() as client:
        df = await client.get_csv("S100WQ4C")
    df
    return


@app.cell
def _(mo):
    button = mo.ui.run_button(label="全銘柄の報告書を取得する")
    button
    return (button,)


@app.cell
async def _(List, button, fetch_csv, mo, pl):
    if button.value:
        lst = List.read().data.filter(pl.col("csvFlag"), pl.col("secCode").is_not_null())
        doc_ids = lst["docID"].unique()
        x = await fetch_csv(doc_ids, limit=100, progress=mo.status.progress_bar)
        mo.output.append(x)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
