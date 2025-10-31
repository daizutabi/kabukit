from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from kabukit.sources.tdnet.columns import ListColumns

if TYPE_CHECKING:
    import datetime

    from kabukit.sources.tdnet.client import TdnetClient

pytestmark = pytest.mark.system


async def test_get_list(client: TdnetClient, date: datetime.date) -> None:
    df1 = await client.get_list(date)
    assert df1.width == 9
    assert df1["Date"].dtype == pl.Date
    assert df1["DisclosedDate"].dtype == pl.Date
    assert df1["DisclosedDate"].eq(date).all()
    assert df1.columns[:3] == ["Date", "Code", "DisclosedDate"]

    date_str = date.strftime("%Y%m%d")
    df2 = await client.get_list(date_str)
    assert_frame_equal(df1, df2)


def test_list_code(data: pl.DataFrame) -> None:
    x = data["Code"]
    assert x.dtype == pl.String
    assert x.is_not_null().all()
    assert x.str.len_chars().min() == 5


def test_list_disclosed_time(data: pl.DataFrame) -> None:
    x = data["DisclosedTime"]
    assert x.dtype == pl.Time
    assert x.is_not_null().all()


def test_list_company(data: pl.DataFrame) -> None:
    x = data["Company"]
    assert x.dtype == pl.String
    assert x.is_not_null().all()


def test_list_title(data: pl.DataFrame) -> None:
    x = data["Title"]
    assert x.dtype == pl.String
    assert x.is_not_null().all()


def test_list_pdf(data: pl.DataFrame) -> None:
    x = data["PdfLink"]
    assert x.dtype == pl.String
    assert x.is_not_null().all()
    assert x.str.ends_with(".pdf").all()


def test_list_xbrl(data: pl.DataFrame) -> None:
    x = data["XbrlLink"]
    assert x.dtype == pl.String
    assert x.drop_nulls().str.ends_with(".zip").all()


def test_list_history(data: pl.DataFrame) -> None:
    x = data["UpdateStatus"]
    assert x.dtype == pl.String


def test_columns(data: pl.DataFrame) -> None:
    assert data.columns == [c.name for c in ListColumns]


def test_rename(data: pl.DataFrame) -> None:
    df_renamed = ListColumns.rename(data, strict=True)
    assert df_renamed.columns == [c.value for c in ListColumns]
