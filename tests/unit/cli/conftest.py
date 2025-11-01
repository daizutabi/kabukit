from __future__ import annotations

import datetime
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import polars as pl
import pytest

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture

MOCK_DF = pl.DataFrame({"A": [1, 2], "B": [3, 4]})
MOCK_CODE = "1234"
MOCK_DATE = "20220101"
MOCK_DATE_OBJ = datetime.date(2022, 1, 1)
MOCK_PATH = "fake/path.csv"


@pytest.fixture
def mock_jquants_client(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("kabukit.sources.jquants.client.JQuantsClient").return_value


@pytest.fixture
def mock_cache_write(mocker: MockerFixture) -> MagicMock:
    mock_cache_write = mocker.patch("kabukit.cli.utils.write")
    mock_cache_write.return_value = MOCK_PATH
    return mock_cache_write
