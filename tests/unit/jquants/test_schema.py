from polars import DataFrame


def test_rename() -> None:
    from kabukit.jquants.schema import rename

    df = DataFrame(
        {
            "Code": ["1"],
            "Open": [1.0],
            "NetSales": [100.0],
        },
    ).pipe(rename)

    assert df.columns == ["銘柄コード", "始値", "売上高"]
