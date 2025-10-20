from __future__ import annotations

import altair as alt
import polars as pl
import pytest

from kabukit.analysis.visualization.market import plot_topix_timeseries

pytestmark = pytest.mark.unit

# pyright: reportArgumentType=false
# pyright: reportUnknownMemberType=false


@pytest.fixture
def sample_topix_df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "Date": ["2024-01-04", "2024-01-05"],
            "Open": [2300, 2350],
            "High": [2380, 2390],
            "Low": [2290, 2340],
            "Close": [2350, 2380],
        },
    )


def test_plot_topix_timeseries(sample_topix_df: pl.DataFrame):
    chart = plot_topix_timeseries(sample_topix_df)
    assert isinstance(chart, alt.Chart)
    assert chart.mark == "line"
    assert chart.encoding.x.shorthand == "Date:T"
    assert chart.encoding.y.shorthand == "Close:Q"
