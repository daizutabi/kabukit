# from __future__ import annotations

# import pytest
# import pytest_asyncio

# from kabukit.sources.tdnet.client import TdnetClient

# pytestmark = pytest.mark.system


# @pytest_asyncio.fixture(scope="module")
# async def dates():
#     client = TdnetClient()
#     yield await client.get_dates()
#     await client.aclose()


# def test_dates(dates: list[datetime.date]) -> None:
#     print(dates)
#     assert 0


# @pytest.mark.asyncio
# async def test_csv(client: EdinetClient) -> None:
#     df = await client.get_csv("S100WKHJ")
#     assert df.columns[0] == "docID"
#     assert df.shape == (47, 10)
#     assert "値" in df.columns
