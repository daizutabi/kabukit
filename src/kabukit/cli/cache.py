"""Cache management commands."""

from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

import typer
from rich.console import Console
from rich.tree import Tree

from kabukit.utils.config import get_cache_dir

if TYPE_CHECKING:
    from pathlib import Path

app = typer.Typer(add_completion=False, help="キャッシュを管理します。")

console = Console()


def add_to_tree(tree: Tree, path: Path) -> None:
    for p in sorted(path.iterdir()):
        if p.is_dir():
            branch = tree.add(f"[bold blue]{p.name}[/bold blue]")
            add_to_tree(branch, p)
        else:
            tree.add(p.name)


@app.command()
def tree() -> None:
    """キャッシュディレクトリのツリー構造を表示します。"""
    cache_dir = get_cache_dir()

    if not cache_dir.exists():
        console.print(f"キャッシュディレクトリ '{cache_dir}' は存在しません。")
        return

    tree_view = Tree(f"[bold green]{cache_dir}[/bold green]")
    add_to_tree(tree_view, cache_dir)
    console.print(tree_view)


@app.command()
def clean() -> None:
    """キャッシュディレクトリを削除します。"""
    cache_dir = get_cache_dir()

    if not cache_dir.exists():
        console.print(f"キャッシュディレクトリ '{cache_dir}' は存在しません。")
        return

    try:
        shutil.rmtree(cache_dir)
        msg = f"キャッシュディレクトリ '{cache_dir}' を正常にクリーンアップしました。"
        console.print(msg)
    except OSError:
        msg = f"キャッシュディレクトリ '{cache_dir}' のクリーンアップ中に"
        msg += "エラーが発生しました。"
        console.print(msg, style="bold red")
        raise typer.Exit(1) from None
