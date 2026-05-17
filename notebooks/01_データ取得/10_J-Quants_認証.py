import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo

    from kabukit import JQuantsClient


@app.cell
def _():
    form = (
        mo.md("{mailaddress}\n\n{password}")
        .batch(
            mailaddress=mo.ui.text(
                kind="email",
                label="メールアドレス",
                placeholder="user@example.com",
            ),
            password=mo.ui.text(kind="password", label="パスワード"),
        )
        .form()
    )
    form
    return (form,)


@app.cell
async def _(form):
    if form.value:
        client = JQuantsClient()
        try:
            token = await client.auth(
                form.value["mailaddress"],
                form.value["password"],
            )
            mo.output.append(mo.md(f"トークンを取得しました: {token[:10]}..."))
        except Exception:
            mo.output.append(mo.md("認証に失敗しました"))
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
