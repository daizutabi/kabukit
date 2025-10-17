from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl
import pytest
from httpx import Response
from polars import DataFrame

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
    df = await client.get_info(clean=False)
    assert df["Date"].to_list() == ["2023-01-01"]
    assert df["Code"].to_list() == ["7203"]


def test_clean() -> None:
    from kabukit.sources.jquants.info import clean

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
