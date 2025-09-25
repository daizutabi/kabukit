import pytest
from polars import DataFrame


def test_dates_days() -> None:
    from kabukit.edinet.concurrent import get_dates

    assert len(get_dates(days=5)) == 5


def test_dates_years() -> None:
    from kabukit.edinet.concurrent import get_dates

    assert len(get_dates(years=1)) in [365, 366]
    assert len(get_dates(years=2)) in [365 + 365, 366 + 365]
    assert len(get_dates(years=4)) == 365 * 4 + 1


def test_dates_error() -> None:
    from kabukit.edinet.concurrent import get_dates

    with pytest.raises(ValueError, match="daysまたはyears"):
        get_dates()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_fetch() -> None:
    from kabukit.edinet.concurrent import fetch

    df = await fetch("list", ["2025-09-09", "2025-09-19", "2025-09-22"])
    assert df.shape == (1231, 30)
    assert df["Date"].n_unique() == 3
    assert df["docID"].n_unique() == 1229  # 重複あり


def callback(df: DataFrame) -> DataFrame:
    assert isinstance(df, DataFrame)
    return df


@pytest.mark.integration
@pytest.mark.asyncio
async def test_fetch_list() -> None:
    from kabukit.edinet.concurrent import fetch_list

    df = await fetch_list(7, limit=6, callback=callback)
    assert df.width == 30


@pytest.mark.integration
@pytest.mark.asyncio
async def test_fetch_csv() -> None:
    from kabukit.edinet.concurrent import fetch, fetch_csv

    df = await fetch("list", ["2025-09-09", "2025-09-19", "2025-09-22"])
    doc_ids = df.filter(csvFlag=True).get_column("docID").sort()
    df = await fetch_csv(doc_ids, limit=10, callback=callback)
    assert df["docID"].n_unique() == 10
