import datetime

import pytest

from kabukit.jquants.client import JQuantsClient

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_get(client: JQuantsClient) -> None:
    df = await client.get_trades_spec()
    assert df.width == 56


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "section",
    [
        "TSE1st",
        "TSE2nd",
        "TSEMothers",
        "TSEJASDAQ",
        "TSEPrime",
        "TSEStandard",
        "TSEGrowth",
        "TokyoNagoya",
    ],
)
async def test_section(client: JQuantsClient, section: str) -> None:
    df = await client.get_trades_spec(section=section)
    assert len(df)
    s = df["Section"].unique()
    assert len(s) == 1
    assert s[0] == section


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "from_",
    [
        "2025-08-01",
        datetime.date(2025, 8, 1),
    ],
)
async def test_from(
    client: JQuantsClient,
    from_: str | datetime.date,
) -> None:
    df = await client.get_trades_spec(from_=from_)
    date = df.item(0, "EndDate")
    assert isinstance(date, datetime.date)
    assert date == datetime.date(2025, 8, 1)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "to",
    [
        "2025-08-01",
        datetime.date(2025, 8, 1),
    ],
)
async def test_to(client: JQuantsClient, to: str | datetime.date) -> None:
    df = await client.get_trades_spec(to=to)
    date = df.item(-1, "EndDate")
    assert isinstance(date, datetime.date)
    assert date == datetime.date(2025, 7, 25)


@pytest.mark.asyncio
async def test_empty(client: JQuantsClient) -> None:
    df = await client.get_trades_spec(from_="2025-01-01", to="2025-01-01")
    assert df.is_empty()
