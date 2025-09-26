import marimo

__generated_with = "0.16.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
    # 財務情報 (`/fins/statements`)

    四半期の財務情報が取得できます。

    <https://jpx.gitbook.io/j-quants-ja/api-reference/statements>
    """,
    )
    return


@app.cell
def _():
    import marimo as mo
    from kabukit import JQuantsClient
    from kabukit.jquants import fetch_all, rename
    return JQuantsClient, fetch_all, mo, rename


@app.cell
async def _(JQuantsClient, rename):
    async with JQuantsClient() as client:
        df = await client.get_statements("1301")
    rename(df)
    return


@app.cell
def _(mo):
    button = mo.ui.run_button(label="全銘柄の財務情報を取得する")
    button
    return (button,)


@app.cell
async def _(button, fetch_all, mo):
    if button.value:
        await fetch_all("statements", limit=100, progress=mo.status.progress_bar)
    return


if __name__ == "__main__":
    app.run()
