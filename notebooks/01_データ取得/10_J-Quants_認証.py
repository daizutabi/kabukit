import marimo

__generated_with = "0.17.6"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # J-QuantsのリフレッシュトークンおよびIDトークンの取得

    [J-Quants](https://jpx-jquants.com/) で登録したEメールアドレスとパスワードを使って、リフレッシュトークンおよびIDトークンを取得します。
    """)
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    form = (
        mo.md("{mailaddress}\n\n{password}")
        .batch(
            mailaddress=mo.ui.text(kind="email", label="メールアドレス", placeholder="user@example.com"),
            password=mo.ui.text(kind="password", label="パスワード"),
        )
        .form()
    )
    form
    return (form,)


@app.cell
async def _(form, mo):
    from kabukit import JQuantsClient

    if form.value:
        client = JQuantsClient()
        try:
            await client.auth(form.value["mailaddress"], form.value["password"])
            mo.output.append(mo.md("トークンを取得しました"))
        except Exception:
            mo.output.append(mo.md("認証に失敗しました"))
    return


if __name__ == "__main__":
    app.run()
