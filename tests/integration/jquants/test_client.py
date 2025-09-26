import datetime

import pytest

from kabukit.jquants.client import JQuantsClient


@pytest.fixture(scope="module")
def date() -> datetime.date:
    today = datetime.date.today()  # noqa: DTZ011
    return today - datetime.timedelta(weeks=12)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_info_date(client: JQuantsClient, date: datetime.date) -> None:
    df = await client.get_info(date=date)
    assert df.height > 4000
    df_date = df.item(0, "Date")
    assert isinstance(df_date, datetime.date)
    assert (df_date - date).days <= 7


@pytest.mark.integration
@pytest.mark.asyncio
async def test_info_code(client: JQuantsClient) -> None:
    df = await client.get_info(code="7203")
    assert df.height == 1
    name = df.item(0, "CompanyName")
    assert isinstance(name, str)
    assert "トヨタ" in name


@pytest.mark.integration
@pytest.mark.asyncio
async def test_prices_code(client: JQuantsClient) -> None:
    df = await client.get_prices(code="7203")
    assert df.width == 16


@pytest.mark.integration
@pytest.mark.asyncio
async def test_prices_date(client: JQuantsClient) -> None:
    df = await client.get_prices(date="2025-08-29")
    assert df.height > 4000
    assert df.height == df["Code"].n_unique()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_prices_empty(client: JQuantsClient) -> None:
    df = await client.get_prices(date="2025-08-30")
    assert df.shape == (0, 0)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_prices_from_to(client: JQuantsClient) -> None:
    df = await client.get_prices(code="7203", from_="2025-08-16", to="2025-08-25")
    assert df.height == 6
    assert df.item(0, "Date") == datetime.date(2025, 8, 18)
    assert df.item(5, "Date") == datetime.date(2025, 8, 25)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_prices_from(client: JQuantsClient) -> None:
    df = await client.get_prices(code="7203", from_="2025-08-16")
    assert df.item(0, "Date") == datetime.date(2025, 8, 18)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_prices_to(client: JQuantsClient) -> None:
    df = await client.get_prices(code="7203", to="2025-08-16")
    assert df.item(-1, "Date") == datetime.date(2025, 8, 15)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_prices_without_code(client: JQuantsClient) -> None:
    df = await client.get_prices()
    assert df.height > 3000


@pytest.mark.integration
@pytest.mark.asyncio
async def test_latest_available_prices(client: JQuantsClient) -> None:
    df = await client.get_latest_available_prices()
    assert df.height > 3000


@pytest.mark.integration
@pytest.mark.asyncio
async def test_latest_available_prices_empty(client: JQuantsClient) -> None:
    df = await client.get_latest_available_prices(0)
    assert df.is_empty()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_statements_code(client: JQuantsClient) -> None:
    df = await client.get_statements(code="7203")
    assert df.width == 75


@pytest.mark.integration
@pytest.mark.asyncio
async def test_statements_date(client: JQuantsClient) -> None:
    df = await client.get_statements(date="2025-08-29")
    assert df.height == 18


@pytest.mark.integration
@pytest.mark.asyncio
async def test_statements_empty(client: JQuantsClient) -> None:
    df = await client.get_statements(date="2025-08-30")
    assert df.shape == (0, 0)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_announcement(client: JQuantsClient) -> None:
    df = await client.get_announcement()
    assert df.width in [7, 0]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_trades_spec(client: JQuantsClient) -> None:
    df = await client.get_trades_spec()
    assert df.width == 56


@pytest.mark.integration
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
async def test_trades_spec_section(client: JQuantsClient, section: str) -> None:
    df = await client.get_trades_spec(section=section)
    assert len(df)
    s = df["Section"].unique()
    assert len(s) == 1
    assert s[0] == section


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "from_",
    [
        "2025-08-01",
        datetime.date(2025, 8, 1),
    ],
)
async def test_trades_spec_from(
    client: JQuantsClient,
    from_: str | datetime.date,
) -> None:
    df = await client.get_trades_spec(from_=from_)
    date = df.item(0, "EndDate")
    assert isinstance(date, datetime.date)
    assert date == datetime.date(2025, 8, 1)


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "to",
    [
        "2025-08-01",
        datetime.date(2025, 8, 1),
    ],
)
async def test_trades_spec_to(client: JQuantsClient, to: str | datetime.date) -> None:
    df = await client.get_trades_spec(to=to)
    date = df.item(-1, "EndDate")
    assert isinstance(date, datetime.date)
    assert date == datetime.date(2025, 7, 25)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_trades_spec_empty(client: JQuantsClient) -> None:
    df = await client.get_trades_spec(from_="2025-01-01", to="2025-01-01")
    assert df.is_empty()
