import marimo

__generated_with = "0.17.6"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # 上場銘柄一覧 (`/listed/info`)

    <https://jpx.gitbook.io/j-quants-ja/api-reference/listed_info>
    """)
    return


@app.cell
def _():
    import marimo as mo
    import polars as pl
    from kabukit import get_info
    return get_info, mo


@app.cell
async def _(get_info):
    await get_info()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
