from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import polars as pl


class BaseColumns(Enum):
    @classmethod
    def rename(cls, df: pl.DataFrame, *, strict: bool = False) -> pl.DataFrame:
        """DataFrameの列名を日本語から英語に変換する。"""
        return df.rename({x.name: x.value for x in cls}, strict=strict)


class ListColumns(BaseColumns):
    Code = "提出者証券コード"  # secCode
    DocumentId = "書類管理番号"  # docID
    DocumentTypeCode = "書類種別コード"  # docTypeCode
    DocumentDescription = "提出書類概要"  # docDescription
    DocumentInfoEditStatus = "書類情報修正区分"  # docInfoEditStatus
    AttachDocumentFlag = "代替書面・添付文書有無フラグ"  # attachDocFlag
    EnglishDocumentFlag = "英文ファイル有無フラグ"  # englishDocFlag
    ParentDocumentId = "親書類管理番号"  # parentDocID
    EdinetCode = "提出者EDINETコード"  # edinetCode
    Jcn = "提出者法人番号"  # JCN
    FilerName = "提出者名"  # filerName
    PeriodStart = "期間(自)"  # periodStart
    PeriodEnd = "期間(至)"  # periodEnd
    SubmitDateTime = "提出日時"  # submitDateTime
    IssuerEdinetCode = "発行会社EDINETコード"  # issuerEdinetCode
    SubjectEdinetCode = "対象EDINETコード"  # subjectEdinetCode
    SubsidiaryEdinetCode = "子会社EDINETコード"  # subsidiaryEdinetCode
    CurrentReportReason = "臨報提出事由"  # currentReportReason
    WithdrawalStatus = "取下区分"  # withdrawalStatus
    DisclosureStatus = "開示不開示区分"  # disclosureStatus
    XbrlFlag = "XBRL有無フラグ"  # xbrlFlag
    PdfFlag = "PDF有無フラグ"  # pdfFlag
    CsvFlag = "CSV有無フラグ"  # csvFlag
    LegalStatus = "縦覧区分"  # legalStatus
    SequenceNumber  = "連番"  # seqNumber
