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
    from kabukit.jquants.schema import rename
    return JQuantsClient, mo, rename


@app.cell
async def _(JQuantsClient, rename):
    async with JQuantsClient() as client:
        df = await client.get_statements(date="20250901")
    rename(df)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
