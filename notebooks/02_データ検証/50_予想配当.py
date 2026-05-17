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
    prices.with_adjusted_shares(statements).with_forecast_dividend(
        statements,
    ).with_dividend_yield().filter(
        # c.Code == "39970"
        c.Code == "7203",
    ).data.select(
        "Date",
        "RawClose",
        "AdjustedIssuedShares",
        "ForecastDividend",
        "DividendPerShare",
        "DividendYield",
    )
    return


@app.cell
def _(prices, statements):
    prices.with_yields(statements).period_stats().filter(c.Code == "7203")
    return


if __name__ == "__main__":
    app.run()
