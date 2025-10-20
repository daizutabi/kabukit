from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_dates_days() -> None:
    from kabukit.utils.date import get_dates

    assert len(get_dates(days=5)) == 5


def test_dates_years() -> None:
    from kabukit.utils.date import get_dates

    assert len(get_dates(years=1)) in [365, 366]
    assert len(get_dates(years=2)) in [365 + 365, 366 + 365]
    assert len(get_dates(years=4)) == 365 * 4 + 1


def test_dates_error() -> None:
    from kabukit.utils.date import get_dates

    with pytest.raises(ValueError, match="daysまたはyears"):
        get_dates()
