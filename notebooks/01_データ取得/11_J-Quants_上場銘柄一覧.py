import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")

with app.setup:
    from kabukit import get_info


@app.cell
async def _():
    await get_info()
    return


if __name__ == "__main__":
    app.run()
