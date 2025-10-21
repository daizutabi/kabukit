from __future__ import annotations

import datetime
from zoneinfo import ZoneInfo


def strpdate(date_string: str, fmt: str | None = None) -> datetime.date:
    """文字列を日付オブジェクトに変換する。

    Args:
        date_string (str): 変換する日付文字列。
        fmt (str | None, optional): 日付文字列のフォーマット。

    Returns:
        datetime.date: 変換された日付オブジェクト。
    """
    if fmt is None:
        fmt = "%Y-%m-%d" if "-" in date_string else "%Y%m%d"

    return (
        datetime.datetime.strptime(date_string, fmt)
        .replace(tzinfo=ZoneInfo("Asia/Tokyo"))
        .date()
    )


def today() -> datetime.date:
    """今日の日付を取得する。

    Returns:
        datetime.date: 今日の日付。
    """
    return datetime.datetime.now(ZoneInfo("Asia/Tokyo")).date()


def get_dates(days: int | None = None, years: int | None = None) -> list[datetime.date]:
    """過去days日またはyears年の日付リストを返す。

    Args:
        days (int | None): 過去days日の日付リストを取得する。
        years (int | None): 過去years年の日付リストを取得する。
            daysが指定されている場合は無視される。
    """
    end_date = today()

    if days is not None:
        start_date = end_date - datetime.timedelta(days=days)
    elif years is not None:
        start_date = end_date.replace(year=end_date.year - years)
    else:
        msg = "daysまたはyearsのいずれかを指定してください。"
        raise ValueError(msg)

    return [
        start_date + datetime.timedelta(days=i)
        for i in range(1, (end_date - start_date).days + 1)
    ]
