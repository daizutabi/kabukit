from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl
import pytest
from polars import DataFrame

if TYPE_CHECKING:
    from unittest.mock import AsyncMock, MagicMock

    from pytest_mock import MockerFixture


def test_clean() -> None:
    from kabukit.jquants.info import clean

    df = DataFrame(
        {
            "Date": ["2023-01-01", "2023-01-02"],
            "ACodeName": ["A", "B"],
            "BCodeName": ["C", "D"],
            "ScaleCategory": ["E", "F"],
            "ACode": ["G", "H"],
            "BCode": ["I", "J"],
            "CompanyNameEnglish": ["K", "L"],
        },
    )

    df = clean(df)
    assert df.shape == (2, 4)
    assert df["Date"].dtype == pl.Date
    assert df["ACodeName"].dtype == pl.Categorical
    assert df["BCodeName"].dtype == pl.Categorical
    assert df["ScaleCategory"].dtype == pl.Categorical


@pytest.fixture
def client(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("kabukit.jquants.client.JQuantsClient").return_value


@pytest.fixture
def get_info(client: MagicMock, mocker: MockerFixture) -> AsyncMock:
    df = DataFrame(
        {
            "Code": ["1301", "1302", "1303", "1304"],
            "MarketCodeName": [
                "グロース",
                "スタンダード",
                "TOKYO PRO MARKET",
                "グロース",
            ],
            "Sector17CodeName": [
                "情報・通信業",
                "その他",
                "サービス業",
                "情報・通信業",
            ],
            "CompanyName": ["A", "B", "C", "A（優先株式）"],  # noqa: RUF001
        },
    )

    get_info = mocker.AsyncMock(return_value=df)
    client.__aenter__.return_value.get_info = get_info
    return get_info


@pytest.mark.asyncio
async def test_get_codes(get_info: AsyncMock) -> None:
    from kabukit.jquants.info import get_target_codes

    codes = await get_target_codes()
    get_info.assert_awaited_once()
    assert codes == ["1301"]
