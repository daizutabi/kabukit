import marimo

__generated_with = "0.15.2"
app = marimo.App(width="medium")

with app.setup:
    from kabukit import JQuantsClient


@app.cell
def _():
    client = JQuantsClient.create()
    client
    return (client,)


@app.cell
def _(client, date):
    client.get_info(date)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
