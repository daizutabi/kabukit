from __future__ import annotations

import datetime
import json
import re
from typing import TYPE_CHECKING

import polars as pl
from bs4 import BeautifulSoup, Tag

from kabukit.utils.datetime import parse_month_day, parse_time, today

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Any


PRELOADED_STATE_PATTERN = re.compile(r"window\.__PRELOADED_STATE__\s*=\s*(\{.*\})")


def get_preloaded_state(text: str) -> dict[str, Any]:
    """HTMLテキストから `__PRELOADED_STATE__` を抽出して辞書として返す。

    Args:
        text: HTMLテキスト。

    Returns:
        抽出した状態辞書。見つからなかった場合は空の辞書。
    """
    soup = BeautifulSoup(text, "lxml")
    script = soup.find("script", string=PRELOADED_STATE_PATTERN)  # pyright: ignore[reportCallIssue, reportArgumentType, reportUnknownVariableType], # ty: ignore[no-matching-overload]

    if not isinstance(script, Tag):
        return {}

    match = PRELOADED_STATE_PATTERN.search(script.text)

    if match is None:
        return {}  # pragma: no cover

    return json.loads(match.group(1))


def parse_quote(text: str) -> pl.DataFrame:
    state = get_preloaded_state(text)

    if not state:
        return pl.DataFrame()

    return pl.DataFrame({"text": [text]})


def iter_press_release(state: dict[str, Any]) -> Iterator[tuple[str, Any]]:
    """状態辞書の mainStocksPressReleaseSummary セクションの主な値を生成する。

    Args:
        state (dict[str, Any]): 状態辞書。

    Yields:
        tuple[str, Any]: mainStocksPressReleaseSummary セクション内の主な値。
    """
    pr: dict[str, Any] = state["mainStocksPressReleaseSummary"]

    yield "PressReleaseSummary", pr["summary"]
    disclosed_datetime = datetime.datetime.fromisoformat(pr["disclosedTime"])
    yield "PressReleaseDisclosedDate", disclosed_datetime.date()
    yield "PressReleaseDisclosedTime", disclosed_datetime.time()


def iter_performance(state: dict[str, Any]) -> Iterator[tuple[str, Any]]:
    """状態辞書の stockPerformance セクションの主な値を生成する。

    Args:
        state (dict[str, Any]): 状態辞書。

    Yields:
        tuple[str, Any]: stockPerformance セクション内の主な値。
    """
    info: dict[str, Any] = state["stockPerformance"]["summaryInfo"]

    yield "PerformanceSummary", info["summary"]
    yield "PerformancePotential", info["potential"]
    yield "PerformanceStability", info["stability"]
    yield "PerformanceProfitability", info["profitability"]
    update_datetime = datetime.datetime.fromisoformat(info["updateTime"])
    yield "PerformanceUpdateDate", update_datetime.date()
    yield "PerformanceUpdateTime", update_datetime.time()


def _parse_datetime(date_str: str) -> tuple[datetime.date, datetime.time]:
    """Yahoo Financeの日付/時刻文字列を解釈する。"""
    if "/" in date_str:
        # "10/29" のような日付形式の場合
        return parse_month_day(date_str), datetime.time(15, 30)  # 取引終了時刻を想定

    # "14:45" のような時刻形式の場合
    return today(), parse_time(date_str)


def iter_price(state: dict[str, Any]) -> Iterator[tuple[str, Any]]:
    """状態辞書から最新の株価を生成する。

    Args:
        state (dict[str, Any]): 状態辞書。

    Yields:
        tuple[str, Any]: 最新の株価と日時。
    """
    detail: dict[str, Any] = state["mainStocksDetail"]["detail"]

    yield "PreviousPrice", float(detail["previousPrice"].replace(",", ""))

    date_str = detail["previousPriceDate"]
    date, time = _parse_datetime(date_str)

    yield "PreviousPriceDate", date
    yield "PreviousPriceTime", time
