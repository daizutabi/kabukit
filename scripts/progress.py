from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import tqdm.asyncio
from rich.progress import Progress

from kabukit.jquants.concurrent import fetch, fetch_all
from kabukit.jquants.info import get_codes

if TYPE_CHECKING:
    from polars import DataFrame


async def main() -> None:
    codes = await get_codes()
    codes = codes[:100]

    with Progress() as progress:
        task_id = progress.add_task("[red]Downloading...", total=len(codes))

        def callback(_: DataFrame) -> None:
            progress.advance(task_id)

        await fetch("statements", codes, callback=callback)

    await fetch_all("statements", limit=100, progress=tqdm.asyncio.tqdm)


if __name__ == "__main__":
    asyncio.run(main())
