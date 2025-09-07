import marimo

__generated_with = "0.15.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
    # 財務情報 (`/fins/statements`)

    <https://jpx.gitbook.io/j-quants-ja/api-reference/statements>
    """
    )
    return


@app.cell
def _():
    import marimo as mo
    from polars import col as c
    from kabukit import JQuantsClient
    return JQuantsClient, mo


@app.cell
def _(JQuantsClient):
    client = JQuantsClient()
    return (client,)


@app.cell
async def _(client):
    await client.get_statements(date="20250904")
    return


@app.cell
async def _(client):
    await client.get_statements(code="1301")
    return


if __name__ == "__main__":
    app.run()
