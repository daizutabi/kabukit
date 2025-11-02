from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app
from kabukit.cli.cache import format_size

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit

runner = CliRunner()


def remove_ansi(text: str) -> str:
    return re.sub(r"\x1B\[[0-?]*[ -/]*[@-~]", "", text)


@pytest.fixture
def mock_get_cache_dir(mocker: MockerFixture, tmp_path: Path) -> MagicMock:
    mock_get_cache_dir = mocker.patch("kabukit.utils.config.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path
    return mock_get_cache_dir


def test_cache_tree(mock_get_cache_dir: MagicMock) -> None:
    cache_dir = mock_get_cache_dir.return_value
    (cache_dir / "info").mkdir()
    (cache_dir / "info" / "test.parquet").touch()

    result = runner.invoke(app, ["cache", "tree"])
    assert result.exit_code == 0

    output = remove_ansi(result.stdout.replace("\n", ""))
    assert str(cache_dir) in output
    assert "info" in result.stdout
    assert "test.parquet" in result.stdout


def test_cache_tree_not_exist(mock_get_cache_dir: MagicMock) -> None:
    mock_get_cache_dir.return_value = Path("/non/existent/path")
    result = runner.invoke(app, ["cache", "tree"])
    assert result.exit_code == 0
    assert "は存在しません" in result.stdout


def test_cache_clean(mock_get_cache_dir: MagicMock, mocker: MockerFixture) -> None:
    cache_dir = mock_get_cache_dir.return_value / "info"
    assert isinstance(cache_dir, Path)
    cache_dir.mkdir()

    mock_rmtree = mocker.patch("shutil.rmtree")

    result = runner.invoke(app, ["cache", "clean", "info"])
    assert result.exit_code == 0
    assert "を正常にクリーンアップしました" in result.stdout

    mock_rmtree.assert_called_once_with(cache_dir)


def test_cache_clean_all(mock_get_cache_dir: MagicMock, mocker: MockerFixture) -> None:
    cache_dir = mock_get_cache_dir.return_value
    assert isinstance(cache_dir, Path)
    (cache_dir / "info").mkdir()

    mock_rmtree = mocker.patch("shutil.rmtree")

    result = runner.invoke(app, ["cache", "clean", "--all"])
    assert result.exit_code == 0
    assert "を正常にクリーンアップしました" in result.stdout

    mock_rmtree.assert_called_once_with(cache_dir)


def test_cache_clean_error(
    mock_get_cache_dir: MagicMock,
    mocker: MockerFixture,
) -> None:
    cache_dir = mock_get_cache_dir.return_value / "info"
    assert isinstance(cache_dir, Path)
    cache_dir.mkdir()
    mock_rmtree = mocker.patch("shutil.rmtree", side_effect=OSError("Test error"))

    result = runner.invoke(app, ["cache", "clean", "info"])
    assert result.exit_code == 1
    output = remove_ansi(result.stdout.replace("\n", ""))
    assert "エラーが発生しました" in output

    mock_rmtree.assert_called_once_with(cache_dir)
    assert cache_dir.exists()


@pytest.mark.parametrize("arg", ["sub_dir", "--all"])
def test_cache_clean_not_exist(mock_get_cache_dir: MagicMock, arg: str) -> None:
    mock_get_cache_dir.return_value = Path("/non/existent/path")
    result = runner.invoke(app, ["cache", "clean", arg])
    assert result.exit_code == 0
    assert "は存在しません" in result.stdout


def test_cache_clean_without_args(mocker: MockerFixture) -> None:
    mock_rmtree = mocker.patch("shutil.rmtree")
    result = runner.invoke(app, ["cache", "clean"])

    assert result.exit_code == 1
    output = remove_ansi(result.stdout.replace("\n", ""))
    assert "--all" in output

    mock_rmtree.assert_not_called()


@pytest.mark.parametrize(
    ("size", "expected"),
    [
        (100, "100B"),
        (2048, "2.0KiB"),
        (5000, "4.9KiB"),
        (5 * 1024**2, "5.0MiB"),
        (312 * 1024**2, "312.0MiB"),
    ],
)
def test_format_size(size: int, expected: str) -> None:
    assert format_size(size) == expected
