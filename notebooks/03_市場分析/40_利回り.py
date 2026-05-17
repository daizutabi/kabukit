import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")

with app.setup:
    from kabukit import Info, Prices


@app.cell
def _():
    Info().data
    return


@app.cell
def _():
    prices = Prices()
    prices.truncate("1mo").data.filter(Code="3997")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
