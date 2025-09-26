import marimo

__generated_with = "0.16.2"
app = marimo.App(width="medium", sql_output="polars")


@app.cell
def _():
    import marimo as mo
    from kabukit import EdinetClient
    return (EdinetClient,)


@app.cell
async def _(EdinetClient):
    async with EdinetClient() as client:
        df = await client.get_csv("S100WQ4C")
    df
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
