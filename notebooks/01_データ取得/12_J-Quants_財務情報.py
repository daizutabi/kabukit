import marimo

__generated_with = "0.17.6"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # 財務情報 (`/fins/statements`)

    四半期の財務情報が取得できます。

    <https://jpx.gitbook.io/j-quants-ja/api-reference/statements>
    """)
    return


@app.cell
def _():
    import marimo as mo
    from kabukit import get_statements
    return get_statements, mo


@app.cell
async def _(get_statements):
    await get_statements("1301")
    return


@app.cell
def _(mo):
    button = mo.ui.run_button(label="全銘柄の財務情報を取得する")
    button
    return (button,)


@app.cell
async def _(button, get_statements, mo):
    if button.value:
        await get_statements(max_items=100, progress=mo.status.progress_bar)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
