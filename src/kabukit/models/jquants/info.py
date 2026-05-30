from __future__ import annotations

from datetime import date  # noqa: TC003

import patito as pt
from pydantic import Field


class InfoModel(pt.Model):
    Date: date = Field(description="日付")
    Code: str = Field(description="銘柄コード")
    Company: str = Field(description="会社名")
    Sector17: str = Field(description="17業種名")
    Sector33: str = Field(description="33業種名")
    ScaleCategory: str = Field(description="規模コード")
    Market: str = Field(description="市場区分名")
    Margin: str = Field(description="貸借信用区分名")


class InfoDataFrame(pt.DataFrame[InfoModel]):
    model: type[InfoModel] = InfoModel
