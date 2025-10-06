from pathlib import Path

from pytest_mock import MockerFixture
from typer.testing import CliRunner

from kabukit.cli.app import app

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

    result = runner.invoke(app, ["cache", "tree"], env={"NO_COLOR": "1"})
    assert result.exit_code == 0
    assert str(tmp_path) in result.stdout
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

    result = runner.invoke(app, ["cache", "clean"])
    assert result.exit_code == 1
    mock_rmtree.assert_called_once_with(tmp_path)
    assert "エラーが発生しました" in result.stdout
