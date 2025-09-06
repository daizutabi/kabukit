from __future__ import annotations

import io
import os
import zipfile
from enum import StrEnum
from typing import TYPE_CHECKING

from httpx import AsyncClient
from lxml import etree
from polars import DataFrame

from kabukit.config import load_dotenv
from kabukit.params import get_params

if TYPE_CHECKING:
    import datetime
    from typing import Any, Self

    from httpx import Response
    from httpx._types import QueryParamTypes

API_VERSION = "v2"
BASE_URL = f"https://api.edinet-fsa.go.jp/api/{API_VERSION}"


class AuthKey(StrEnum):
    """Environment variable keys for EDINET authentication."""

    API_KEY = "EDINET_API_KEY"


class EdinetClient:
    client: AsyncClient

    def __init__(self, client: AsyncClient) -> None:
        self.client = client

    @classmethod
    def create(cls) -> Self:
        load_dotenv()
        api_key = os.getenv(AuthKey.API_KEY)
        if not api_key:
            msg = "EDINET_API_KEY is not set."
            raise KeyError(msg)
        params = {"Subscription-Key": api_key}
        client = AsyncClient(base_url=BASE_URL, params=params)
        return cls(client)

    async def aclose(self) -> None:
        await self.client.aclose()

    async def get(self, url: str, params: QueryParamTypes) -> Response:
        resp = await self.client.get(url, params=params)
        resp.raise_for_status()
        return resp

    async def get_count(self, date: str | datetime.date) -> int:
        params = get_params(date=date, type=1)
        resp = await self.get("/documents.json", params)
        data = resp.json()
        metadata = data["metadata"]

        if metadata["status"] != "200":
            return 0

        return metadata["resultset"]["count"]

    async def get_list(self, date: str | datetime.date) -> DataFrame:
        params = get_params(date=date, type=2)
        resp = await self.get("/documents.json", params)
        data = resp.json()

        if "results" not in data:
            return DataFrame()

        return DataFrame(data["results"], infer_schema_length=None)

    async def get_document(self, doc_id: str, doc_type: int) -> Response:
        params = get_params(type=doc_type)
        return await self.get(f"/documents/{doc_id}", params)

    async def get_pdf(self, doc_id: str) -> bytes:
        resp = await self.get_document(doc_id, doc_type=2)
        if resp.headers["content-type"] == "application/pdf":
            return resp.content

        msg = "PDF is not available."
        raise ValueError(msg)

    async def get_zip(self, doc_id: str, doc_type: int) -> bytes:
        resp = await self.get_document(doc_id, doc_type=doc_type)
        if resp.headers["content-type"] == "application/octet-stream":
            return resp.content

        msg = "ZIP is not available."
        raise ValueError(msg)

    def parse_xbrl(self, xbrl_content: bytes) -> dict[str, Any]:
        parser = etree.XMLParser(recover=True)
        tree = etree.fromstring(xbrl_content, parser)
        ns = {
            k if k is not None else "xbrli": v
            for k, v in tree.nsmap.items()
            if k is not None
        }
        ns["jppfs_cor"] = (
            "http://disclosure.edinet-fsa.go.jp/taxonomy/jppfs/2022-11-01/jppfs_cor"
        )

        net_sales_element = tree.find(".//jppfs_cor:NetSales", namespaces=ns)
        if net_sales_element is not None and net_sales_element.text is not None:
            context_ref = net_sales_element.get("contextRef")
            context = tree.find(f".//xbrli:context[@id='{context_ref}']", namespaces=ns)
            if context is not None:
                period = context.find(".//xbrli:period", namespaces=ns)
                if period is not None:
                    instant = period.find(".//xbrli:instant", namespaces=ns)
                    if instant is not None:
                        period_val = instant.text
                    else:
                        start_date = period.find(".//xbrli:startDate", namespaces=ns)
                        end_date = period.find(".//xbrli:endDate", namespaces=ns)
                        period_val = f"{start_date.text if start_date is not None else ''} - {end_date.text if end_date is not None else ''}"
                else:
                    period_val = None

                scenario = context.find(".//xbrli:scenario", namespaces=ns)

                return {
                    "NetSales": net_sales_element.text,
                    "context": {
                        "id": context.get("id"),
                        "period": period_val,
                        "consolidated": scenario is None,
                    },
                }
        return {}
