import altair as alt
import polars as pl
import pytest

from kabukit.analysis.visualization import (
    plot_prices,
    plot_prices_candlestick,
    plot_prices_volume,
)
from kabukit.core.prices import Prices


@pytest.fixture
def sample_prices() -> Prices:
    df = pl.DataFrame(
        {
            "Date": ["2024-01-04", "2024-01-05"],
            "Open": [100, 110],
            "High": [120, 120],
            "Low": [90, 100],
            "Close": [110, 100],
            "Volume": [1000, 2000],
        },
    )
    return Prices(df)


def test_plot_prices(sample_prices: Prices):
    chart = plot_prices(sample_prices)
    assert isinstance(chart, alt.VConcatChart)
    assert len(chart.vconcat) == 2


def test_plot_prices_unsupported_kind(sample_prices: Prices):
    with pytest.raises(NotImplementedError):
        plot_prices(sample_prices, kind="line")  # pyright: ignore[reportArgumentType]


def test_plot_prices_candlestick(sample_prices: Prices):
    chart = plot_prices_candlestick(sample_prices)
    assert isinstance(chart, alt.LayerChart)
    assert len(chart.layer) == 2
    assert chart.encoding.x.shorthand == "Date:T"  # pyright: ignore[reportUnknownMemberType]
    assert chart.encoding.y["title"] == "株価"  # pyright: ignore[reportUnknownMemberType]


def test_plot_prices_volume(sample_prices: Prices):
    chart = plot_prices_volume(sample_prices)
    assert isinstance(chart, alt.Chart)
    assert chart.mark == "bar"  # pyright: ignore[reportUnknownMemberType]
    assert chart.encoding.x.shorthand == "Date:T"  # pyright: ignore[reportUnknownMemberType]
    assert chart.encoding.y.shorthand == "Volume:Q"  # pyright: ignore[reportUnknownMemberType]
