from pathlib import Path

import pytest
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from kabukit.cli.app import app

pytestmark = pytest.mark.unit

runner = CliRunner()


def test_cache_tree_not_exist(mocker: MockerFixture) -> None:
    mock_get_cache_dir = mocker.patch("kabukit.cli.cache.get_cache_dir")
    mock_get_cache_dir.return_value = Path("/non/existent/path")
    result = runner.invoke(app, ["cache", "tree"])
    assert result.exit_code == 0
    assert "は存在しません" in result.stdout


def test_cache_tree_exists(mocker: MockerFixture, tmp_path: Path) -> None:
    mock_get_cache_dir = mocker.patch("kabukit.cli.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path
    (tmp_path / "info").mkdir()
    (tmp_path / "info" / "test.parquet").touch()

    result = runner.invoke(app, ["cache", "tree"])
    assert result.exit_code == 0
    assert str(tmp_path) in result.stdout.replace("\n", "")
    assert "info" in result.stdout
    assert "test.parquet" in result.stdout


def test_cache_clean_not_exist(mocker: MockerFixture) -> None:
    mock_get_cache_dir = mocker.patch("kabukit.cli.cache.get_cache_dir")
    mock_get_cache_dir.return_value = Path("/non/existent/path")
    result = runner.invoke(app, ["cache", "clean"])
    assert result.exit_code == 0
    assert "は存在しません" in result.stdout


def test_cache_clean_exists(mocker: MockerFixture, tmp_path: Path) -> None:
    mock_get_cache_dir = mocker.patch("kabukit.cli.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path
    mock_rmtree = mocker.patch("shutil.rmtree")
    (tmp_path / "info").mkdir()

    result = runner.invoke(app, ["cache", "clean"])
    assert result.exit_code == 0
    mock_rmtree.assert_called_once_with(tmp_path)
    assert "を正常にクリーンアップしました" in result.stdout


def test_cache_clean_error(mocker: MockerFixture, tmp_path: Path) -> None:
    mock_get_cache_dir = mocker.patch("kabukit.cli.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path
    mock_rmtree = mocker.patch("shutil.rmtree", side_effect=OSError("Test error"))
    (tmp_path / "info").mkdir()

    result = runner.invoke(app, ["cache", "clean"], env={"NO_COLOR": "1"})
    assert result.exit_code == 1
    mock_rmtree.assert_called_once_with(tmp_path)
    assert "エラーが発生しました" in result.stdout


@pytest.mark.parametrize(
    ("size", "expected"),
    [
        (100, "100 B"),
        (2048, "2.0 KB"),
        (5000, "4.9 KB"),
        (5 * 1024**2, "5.0 MB"),
        (312 * 1024**2, "312.0 MB"),
    ],
)
def test_format_size(size: int, expected: str) -> None:
    from kabukit.cli.cache import format_size

    assert format_size(size) == expected
