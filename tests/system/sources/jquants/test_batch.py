from __future__ import annotations

import datetime

import polars as pl
import pytest

from kabukit.sources.jquants.batch import (
    get_calendar,
    get_info,
    get_prices,
    get_statements,
    get_target_codes,
)

pytestmark = pytest.mark.system


async def test_get_calender() -> None:
    df = await get_calendar()
    df = df.filter(pl.col("IsHoliday"))
    assert datetime.date(2026, 12, 31) in df["Date"]


async def test_get_info() -> None:
    df = await get_info()
    assert df["Date"].n_unique() == 1
    assert "72030" in df["Code"]
    assert "99840" in df["Code"]


async def test_get_info_with_code() -> None:
    df = await get_info("7203")
    assert "72030" in df["Code"]
    assert df.height == 1


async def test_get_info_with_date() -> None:
    df = await get_info(date="2025-10-22")
    assert df["Date"].unique().to_list() == [datetime.date(2025, 10, 22)]
    assert "72030" in df["Code"]
    assert "99840" in df["Code"]


async def test_get_info_with_code_date() -> None:
    df = await get_info("7203", "2025-10-22")
    assert df["Date"].unique().to_list() == [datetime.date(2025, 10, 22)]
    assert "72030" in df["Code"]
    assert df.height == 1


async def test_get_target_codes() -> None:
    codes = await get_target_codes()
    assert "72030" in codes
    assert "99840" in codes


async def test_get_target_codes_all_ends_with_zero() -> None:
    codes = await get_target_codes()
    assert all(code.endswith("0") for code in codes)


async def test_get_statements() -> None:
    df = await get_statements(max_items=3)
    assert df["Code"].n_unique() == 3


async def test_get_statements_with_code() -> None:
    df = await get_statements("7203")
    assert df["Date"].n_unique() > 40
    assert df["Code"].unique().to_list() == ["72030"]


async def test_get_statements_with_date() -> None:
    df = await get_statements(date="2025-10-21")
    assert df["DisclosedDate"].unique().to_list() == [datetime.date(2025, 10, 21)]
    assert df["Date"].unique().sort().to_list() == [
        datetime.date(2025, 10, 21),
        datetime.date(2025, 10, 22),
    ]
    assert "30910" in df["Code"]
    assert "99140" in df["Code"]


async def test_get_statements_with_codes() -> None:
    df = await get_statements(["7203", "6758"])
    assert sorted(df["Code"].unique()) == ["67580", "72030"]


async def test_get_statements_with_max_items() -> None:
    df = await get_statements(["7203", "6758"], max_items=1)
    assert df["Code"].unique().to_list() == ["72030"]


async def test_get_prices() -> None:
    df = await get_prices(max_items=3)
    assert df["Code"].n_unique() == 3


async def test_get_prices_with_code() -> None:
    df = await get_prices("7203")
    assert df["Code"].unique().to_list() == ["72030"]
    assert df["Date"].n_unique() > 2000


async def test_get_prices_with_date() -> None:
    df = await get_prices(date="2025-10-22")
    assert df["Date"].unique().to_list() == [datetime.date(2025, 10, 22)]
    assert df["Code"].n_unique() > 3000


async def test_get_prices_with_codes() -> None:
    df = await get_prices(["7203", "6758"])
    assert sorted(df["Code"].unique()) == ["67580", "72030"]


async def test_get_prices_with_max_items() -> None:
    df = await get_prices(["7203", "6758"], max_items=1)
    assert df["Code"].unique().to_list() == ["72030"]
