from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl
import pytest
from httpx import Response

from kabukit.sources.jquants.client import JQuantsClient

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_info(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    json = {"info": [{"Date": "2023-01-01", "Code": "7203"}]}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    df = await client.get_info(clean=False, only_common_stocks=False)
    assert df["Date"].to_list() == ["2023-01-01"]
    assert df["Code"].to_list() == ["7203"]


@pytest.mark.asyncio
async def test_get_info_only_common_stocks(
    mock_get: AsyncMock,
    mocker: MockerFixture,
) -> None:
    json = {"info": [{"Code": "7203"}, {"Code": "9999"}]}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    mock_filter_common_stocks = mocker.patch(
        "kabukit.sources.jquants.client.info.filter_common_stocks",
        return_value=pl.DataFrame({"Code": ["7203"]}),
    )

    client = JQuantsClient("test_token")
    df = await client.get_info(clean=False, only_common_stocks=True)
    assert df["Code"].to_list() == ["7203"]
    mock_filter_common_stocks.assert_called_once()


def test_clean() -> None:
    from kabukit.sources.jquants.clean.info import clean

    df = pl.DataFrame(
        {
            "Date": ["2023-01-01", "2023-01-02"],
            "CompanyName": ["A", "B"],
            "Sector17CodeName": ["A", "B"],
            "Sector33CodeName": ["C", "D"],
            "ScaleCategory": ["E", "F"],
            "MarketCodeName": ["G", "H"],
            "MarginCodeName": ["I", "J"],
            "CompanyNameEnglish": ["K", "L"],
        },
    )

    df = clean(df)
    assert df.shape == (2, 7)
    assert df["Date"].dtype == pl.Date
    assert df["Company"].dtype == pl.String
    assert df["Sector17"].dtype == pl.Categorical
    assert df["Sector33"].dtype == pl.Categorical
    assert df["ScaleCategory"].dtype == pl.Categorical
    assert df["Market"].dtype == pl.Categorical
    assert df["Margin"].dtype == pl.Categorical


def test_filter_common_stocks() -> None:
    from kabukit.sources.jquants.clean.info import filter_common_stocks

    df = pl.DataFrame(
        {
            "Code": ["0001", "0002", "0003", "0004", "0005"],
            "MarketCodeName": [
                "プライム",
                "TOKYO PRO MARKET",  # フィルタリング対象
                "スタンダード",
                "グロース",
                "プライム",
            ],
            "Sector17CodeName": [
                "情報・通信業",
                "サービス業",
                "その他",  # フィルタリング対象
                "小売業",
                "銀行業",
            ],
            "CompanyName": [
                "A社",
                "B社",
                "C社",
                "D（優先株式）",  # フィルタリング対象
                "E社",
            ],
        },
    )

    result = filter_common_stocks(df)
    assert result["Code"].to_list() == ["0001", "0005"]
