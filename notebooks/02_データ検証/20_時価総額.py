import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")

with app.setup:
    from polars import col as c

    from kabukit import Prices, Statements


@app.cell
def _():
    statements = Statements()
    prices = Prices()
    return prices, statements


@app.cell
def _(prices, statements):
    prices.with_adjusted_shares(statements).with_market_cap().filter(
        c.Code == "3997",
    ).data.select(
        "Date",
        "RawClose",
        "AdjustedIssuedShares",
        "AdjustedTreasuryShares",
        "MarketCap",
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
