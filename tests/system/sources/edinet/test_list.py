from __future__ import annotations

import datetime

import polars as pl
import pytest
import pytest_asyncio

from kabukit.sources.edinet.client import EdinetClient

pytestmark = pytest.mark.system


@pytest.mark.asyncio
async def test_list(client: EdinetClient) -> None:
    df = await client.get_list("2025-09-04")
    assert df.shape == (76, 25)
    assert df.columns[0] == "Date"
    assert df["Date"].dtype == pl.Date
    assert df.columns[-1] == "FileDate"
    assert df["FileDate"].dtype == pl.Date
    assert df["FileDate"].unique().to_list() == [datetime.date(2025, 9, 4)]


@pytest.mark.asyncio
async def test_list_invalid_date(client: EdinetClient) -> None:
    df = await client.get_list("1000-01-01")
    assert df.shape == (0, 0)


@pytest.mark.asyncio
async def test_list_holiday(client: EdinetClient) -> None:
    df = await client.get_list("2025-09-23")
    assert df.shape == (0, 0)


@pytest_asyncio.fixture(scope="module")
async def data():
    client = EdinetClient()
    yield await client.get_list("2025-06-27")
    await client.aclose()


def test_xbrl_csv(data: pl.DataFrame) -> None:
    df = data.filter(XbrlFlag="1")
    assert df.height == df.filter(CsvFlag="1").height


def test_df_xbrl_pdf(data: pl.DataFrame) -> None:
    df = data.filter(XbrlFlag="1")
    assert df.height == df.filter(PdfFlag="1").height


def test_columns(data: pl.DataFrame) -> None:
    from kabukit.sources.edinet.columns import ListColumns

    assert data.columns == [c.name for c in ListColumns]


def test_rename(data: pl.DataFrame) -> None:
    from kabukit.sources.edinet.columns import ListColumns

    df_renamed = ListColumns.rename(data, strict=True)
    assert df_renamed.columns == [c.value for c in ListColumns]
