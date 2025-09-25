from datetime import date

import pytest


def test_iter_items() -> None:
    from kabukit.utils.params import iter_items

    a, from_ = iter_items({"a": 1, "b": None, "from_": "2023-01-01"})
    assert a == ("a", 1)
    assert from_ == ("from", "2023-01-01")


def test_get_items() -> None:
    from kabukit.utils.params import get_params

    params = get_params(a=1, b=None, c="c", from_=date(2023, 1, 1))
    assert len(params) == 3
    assert params["a"] == "1"
    assert params["c"] == "c"
    assert params["from"] == "2023-01-01"


@pytest.mark.parametrize("d", ["2023-01-01", date(2023, 1, 1)])
def test_date_to_str(d: str | date) -> None:
    from kabukit.utils.params import date_to_str

    assert date_to_str(d) == "2023-01-01"
