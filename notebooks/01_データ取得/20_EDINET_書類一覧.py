import marimo

__generated_with = "0.16.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import datetime
    from kabukit import EdinetClient
    from kabukit.utils.concurrent import collect_fn
    return EdinetClient, datetime


@app.cell
def _(datetime):
    today = datetime.date.today()
    return (today,)


@app.cell
def _():
    return


@app.cell
def _(datetime, today):
    async def fetch_list(days: int):
        dates = sorted(today - datetime.timedelta(days=d) for d in range(10))
    return


@app.cell
def _(EdinetClient):
    client = EdinetClient()
    return (client,)


@app.cell
async def _(client):
    await client.get_list("2022-01-01")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
