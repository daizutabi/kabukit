from __future__ import annotations

import polars as pl
import typer
from rich.console import Console
from rich.table import Table


def display_single_row_dataframe(df: pl.DataFrame) -> None:
    """DataFrameが単一行の場合、rich Tableで整形して表示します。"""

    table = Table(
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Column Name", style="cyan", no_wrap=True)
    table.add_column("Data Type", style="yellow")
    table.add_column("Value", style="green")

    for col_name, dtype in df.schema.items():
        value = df[0, col_name]
        table.add_row(col_name, str(dtype), str(value))

    console = Console()
    console.print(table)


def display_dataframe(df: pl.DataFrame) -> None:
    """データフレームを表示します。"""
    pl.Config.set_tbl_rows(5)
    pl.Config.set_tbl_cols(6)
    pl.Config.set_tbl_hide_dtype_separator()

    if df.is_empty():
        typer.echo("取得したデータはありません。")
    elif df.height == 1:
        display_single_row_dataframe(df)
    else:
        typer.echo(df)
