from __future__ import annotations

import polars as pl
import typer
from rich import box
from rich.console import Console
from rich.table import Table


def display_dataframe(
    df: pl.DataFrame,
    *,
    first: bool = False,
    last: bool = False,
    quiet: bool = False,
) -> None:
    """データフレームを表示します。"""
    if quiet:
        return

    pl.Config.set_tbl_rows(5)
    pl.Config.set_tbl_cols(6)
    pl.Config.set_tbl_hide_dtype_separator()

    if df.is_empty():
        typer.echo("取得したデータはありません。")
    elif df.height == 1:
        display_single_row_dataframe(df)
    elif first:
        display_single_row_dataframe(df.head(1))
    elif last:
        display_single_row_dataframe(df.tail(1))
    else:
        typer.echo(df)


def display_single_row_dataframe(df: pl.DataFrame) -> None:
    """DataFrameが単一行の場合、rich Tableで整形して表示します。"""
    typer.echo(f"width: {df.width}")

    table = Table(show_header=True, header_style=None, box=box.SQUARE_DOUBLE_HEAD)

    table.add_column("Column Name", no_wrap=True)
    table.add_column("Data Type")
    table.add_column("Value")

    for col_name, dtype in df.schema.items():
        value = df[0, col_name]
        table.add_row(col_name, str(dtype), str(value))

    console = Console()
    console.print(table)
