import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")

with app.setup:
    from polars import col as c

    from kabukit import Info, Prices, Statements


@app.cell
def _():
    Info().data.filter(c.Code == "6200")
    return


@app.cell
def _():
    statements = Statements()
    prices = Prices().with_adjusted_shares(statements)
    return (prices,)


@app.cell
def _(prices):
    prices.data.filter(c.Code == "3997").select(
        "Date",
        "Close",
        "RawClose",
        "AdjustmentFactor",
        "AdjustedIssuedShares",
    )
    return


if __name__ == "__main__":
    app.run()
