from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl
import pytest
from polars.testing import assert_frame_equal
from typer.testing import CliRunner

from kabukit.cli.app import app

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.integration

runner = CliRunner()


@pytest.fixture
def mock_cache_dir(tmp_path: Path, mocker: MockerFixture) -> Path:
    """Create a temporary cache directory and mock get_cache_dir for tests."""
    # For integration tests, we want to mock the cache directory to a temporary path
    # to avoid polluting the actual cache and ensure test isolation.
    mocker.patch("kabukit.domain.cache.get_cache_dir", return_value=tmp_path)
    return tmp_path


def test_get_info_with_code(mocker: MockerFixture):
    mock_df = pl.DataFrame({"code": ["1234"], "name": ["test"]})
    mock_get = mocker.patch(
        "kabukit.sources.jquants.client.JQuantsClient.get_info",
        return_value=mock_df,
    )
    result = runner.invoke(app, ["get", "info", "1234"])
    assert result.exit_code == 0
    assert "test" in result.stdout
    mock_get.assert_called_once_with("1234")


def test_get_info_all(mocker: MockerFixture, mock_cache_dir: Path):
    mock_df = pl.DataFrame({"code": ["1234"], "name": ["test"]})
    mock_get = mocker.patch(
        "kabukit.sources.jquants.client.JQuantsClient.get_info",
        return_value=mock_df,
    )
    result = runner.invoke(app, ["get", "info"])
    assert result.exit_code == 0
    assert "全銘柄の情報を" in result.stdout
    assert mock_get.call_count == 1

    path = next(mock_cache_dir.joinpath("jquants", "info").glob("*.parquet"))
    assert_frame_equal(pl.read_parquet(path), mock_df)


def test_get_statements_all(mocker: MockerFixture, mock_cache_dir: Path):
    mock_df = pl.DataFrame({"code": ["1234"], "Profit": [100]})
    mock_get_statements = mocker.patch(
        "kabukit.sources.jquants.concurrent.get_statements",
        return_value=mock_df,
    )
    result = runner.invoke(app, ["get", "statements"])
    assert result.exit_code == 0
    assert "全銘柄の財務情報を" in result.stdout
    mock_get_statements.assert_called_once_with(
        None,
        max_items=None,
        progress=mocker.ANY,
    )

    path = next(mock_cache_dir.joinpath("jquants", "statements").glob("*.parquet"))
    assert_frame_equal(pl.read_parquet(path), mock_df)


def test_get_prices_all(mocker: MockerFixture, mock_cache_dir: Path):
    mock_df = pl.DataFrame({"code": ["1234"], "Close": [1000]})
    mock_get_prices = mocker.patch(
        "kabukit.sources.jquants.concurrent.get_prices",
        return_value=mock_df,
    )
    result = runner.invoke(app, ["get", "prices"])
    assert result.exit_code == 0
    assert "全銘柄の株価情報を" in result.stdout

    mock_get_prices.assert_called_once_with(None, max_items=None, progress=mocker.ANY)

    path = next(mock_cache_dir.joinpath("jquants", "prices").glob("*.parquet"))
    assert_frame_equal(pl.read_parquet(path), mock_df)


def test_get_edinet_list_all(mocker: MockerFixture, mock_cache_dir: Path):
    mock_df = pl.DataFrame({"docID": ["doc1"], "filerName": ["test"]})
    mock_get_edinet_list = mocker.patch(
        "kabukit.sources.edinet.concurrent.get_list",
        return_value=mock_df,
    )
    result = runner.invoke(app, ["get", "edinet"])
    assert result.exit_code == 0
    assert "書類一覧を" in result.stdout

    mock_get_edinet_list.assert_called_once_with(
        None,
        years=10,
        progress=mocker.ANY,
        max_items=None,
    )

    path = next(mock_cache_dir.joinpath("edinet", "list").glob("*.parquet"))
    assert_frame_equal(pl.read_parquet(path), mock_df)
