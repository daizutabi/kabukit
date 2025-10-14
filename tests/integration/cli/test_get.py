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


def test_get_info_with_code(mocker: MockerFixture):
    mock_df = pl.DataFrame({"code": ["1234"], "name": ["test"]})
    mock_get = mocker.patch(
        "kabukit.jquants.client.JQuantsClient.get_info", return_value=mock_df
    )
    result = runner.invoke(app, ["get", "info", "1234"])
    assert result.exit_code == 0
    assert "test" in result.stdout
    mock_get.assert_called_once_with("1234")


def test_get_info_all(mocker: MockerFixture, mock_cache_dir: Path):
    mock_df = pl.DataFrame({"code": ["1234"], "name": ["test"]})
    mock_get = mocker.patch(
        "kabukit.jquants.client.JQuantsClient.get_info", return_value=mock_df
    )
    result = runner.invoke(app, ["get", "info"])
    assert result.exit_code == 0
    assert "全銘柄の情報を" in result.stdout
    assert mock_get.call_count == 1

    path = next(mock_cache_dir.joinpath("info").glob("*.parquet"))
    assert_frame_equal(pl.read_parquet(path), mock_df)


def test_get_statements_all(mocker: MockerFixture, mock_cache_dir: Path):
    mock_df = pl.DataFrame({"code": ["1234"], "Profit": [100]})
    mock_get_statements = mocker.patch(
        "kabukit.jquants.concurrent.get_statements", return_value=mock_df
    )  # Changed mock
    result = runner.invoke(app, ["get", "statements"])
    assert result.exit_code == 0
    assert "全銘柄の財務情報を" in result.stdout
    mock_get_statements.assert_called_once_with(
        None, limit=None, progress=mocker.ANY
    )  # Updated assertion

    path = next(mock_cache_dir.joinpath("statements").glob("*.parquet"))
    assert_frame_equal(pl.read_parquet(path), mock_df)


def test_get_prices_all(mocker: MockerFixture, mock_cache_dir: Path):
    mock_df = pl.DataFrame({"code": ["1234"], "Close": [1000]})
    mock_get_prices = mocker.patch(
        "kabukit.jquants.concurrent.get_prices", return_value=mock_df
    )  # Changed mock
    result = runner.invoke(app, ["get", "prices"])
    assert result.exit_code == 0
    assert "全銘柄の株価情報を" in result.stdout
    mock_get_prices.assert_called_once_with(
        None, limit=None, progress=mocker.ANY
    )  # Updated assertion

    path = next(mock_cache_dir.joinpath("prices").glob("*.parquet"))
    assert_frame_equal(pl.read_parquet(path), mock_df)


def test_get_entries_all(mocker: MockerFixture, mock_cache_dir: Path):
    mock_df = pl.DataFrame({"docID": ["doc1"], "filerName": ["test"]})
    mock_get = mocker.patch(
        "kabukit.edinet.concurrent.get_entries", return_value=mock_df
    )
    result = runner.invoke(app, ["get", "entries"])
    assert result.exit_code == 0
    assert "書類一覧を" in result.stdout
    mock_get.assert_called_once_with(None, years=10, progress=mocker.ANY)

    path = next(mock_cache_dir.joinpath("entries").glob("*.parquet"))
    assert_frame_equal(pl.read_parquet(path), mock_df)
