import marimo

__generated_with = "0.15.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import asyncio
    import marimo as mo
    from collections.abc import AsyncIterator


    async def asleep(time: int) -> int:
        await asyncio.sleep(time)
        return time


    async def async_iter(times: list[int]) -> AsyncIterator[int]:
        async for future in asyncio.as_completed(asleep(time) for time in times):
            yield await future
    return async_iter, mo


@app.cell
async def _(async_iter, mo):
    with mo.status.progress_bar(total=3) as bar:
        async for _ in async_iter([3, 2, 1]):
            bar.update()
    return


@app.cell
def _(mo):
    class progress_bar_async(mo.status.progress_bar):
        async def __aiter__(self):
            async for item in self.collection:
                yield item

                if not self.disabled:
                    self.progress.update(increment=self.step)
            self._finish()
    return (progress_bar_async,)


@app.cell
async def _(async_iter, progress_bar_async):
    result1 = []
    async for time in progress_bar_async(async_iter([3, 2, 1]), total=3):
        result1.append(time)
    return


@app.cell
async def _(async_iter, progress_bar_async):
    result2 = [time async for time in progress_bar_async(async_iter([3, 2, 1]), total=3)]
    return


@app.cell
def _(async_iter):
    from collections.abc import Collection, AsyncIterable, Iterable

    isinstance(async_iter([3, 2, 1]), Collection)
    return Collection, Iterable


@app.cell
def _(Iterable, async_iter):
    isinstance(async_iter([3, 2, 1]), Iterable)
    return


@app.cell
def _(mo):
    it = (x for x in range(10))
    for x in mo.status.progress_bar(it,total=3):
        pass
    return (it,)


@app.cell
def _(Collection, it):
    isinstance(it, Collection)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
