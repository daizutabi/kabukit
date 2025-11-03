from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from kabukit.sources.edinet.client import EdinetClient

pytestmark = pytest.mark.system


async def test_pdf(client: EdinetClient) -> None:
    df = await client.get_pdf("S100WKHJ")
    content = df.item(0, "PdfContent")
    assert isinstance(content, bytes)
    assert content.startswith(b"%PDF-")


async def test_pdf_error(client: EdinetClient) -> None:
    with pytest.raises(ValueError, match="PDF is not available"):
        await client.get_pdf("S100WMS8")


async def test_zip(client: EdinetClient) -> None:
    assert await client.get_zip("S100WKHJ", doc_type=5) is not None


async def test_zip_error(client: EdinetClient) -> None:
    with pytest.raises(ValueError, match="ZIP is not available"):
        await client.get_zip("S100WM0M", doc_type=5)


async def test_csv(client: EdinetClient) -> None:
    df = await client.get_csv("S100WKHJ")
    assert df.columns[0] == "DocumentId"
    assert df.shape == (47, 10)
    assert "値" in df.columns


async def test_xbrl(client: EdinetClient) -> None:
    xbrl = await client.get_xbrl("S100WXPV")
    assert xbrl.startswith('<?xml version="1.0" encoding="UTF-8"?>\n<xbrli:xbrl')
