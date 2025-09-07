import marimo as mo
import polars as pl
import asyncio
import datetime

from kabukit.edinet.client import EdinetClient
from kabukit.jquants.client import JQuantsClient

# --- API Key Setup Reminder ---
mo.md(
    """
# 00. 全API探索ノートブック

このノートブックを実行する前に、EDINETとJ-QuantsのAPIキーが設定されていることを確認してください。

**EDINET APIキー:**
環境変数 `EDINET_API_KEY` に設定するか、`EdinetClient.create()` の前に `kabukit.config.load_dotenv()` を呼び出してください。

**J-Quants APIキー:**
J-Quantsの認証は、`JQuantsClient.auth()` メソッドを使って行います。
一度認証が成功すれば、トークンが保存され、次回以降は自動的にロードされます。
まだ認証を行っていない場合は、以下のコードを実行して認証してください。
```python
# import asyncio
# from kabukit.jquants.client import JQuantsClient
# async def setup_jquants_auth():
#     client = JQuantsClient.create()
#     try:
#         # Replace with your J-Quants mailaddress and password
#         await client.auth(mailaddress="YOUR_JQUANTS_EMAIL", password="YOUR_JQUANTS_PASSWORD")
#         print("J-Quants authentication successful!")
#     except Exception as e:
#         print(f"J-Quants authentication failed: {e}")
#     finally:
#         await client.aclose()
# asyncio.run(setup_jquants_auth())
```
---
")

async def explore_edinet_apis():
    mo.md("## EDINET API 探索")
    client = EdinetClient.create()
    results = []
    try:
        # --- get_count ---
        today = datetime.date.today()
        try:
            count = await client.get_count(today)
            results.append(f"### `client.get_count('{today}')`")
            results.append(f"今日の提出文書数: {count}")
        except Exception as e:
            results.append(f"### `client.get_count('{today}')`")
            results.append(f"エラー: {e}")

        # --- get_list ---
        try:
            df_list = await client.get_list(today)
            results.append(f"### `client.get_list('{today}')`")
            results.append(f"提出文書リスト (shape: {df_list.shape}):")
            results.append(mo.as_html(df_list.head()))
            
            # Find a doc_id with CSV and PDF for further tests
            sample_doc_id_csv = None
            sample_doc_id_pdf = None
            if not df_list.is_empty():
                csv_docs = df_list.filter(pl.col("csvFlag") == "1")
                if not csv_docs.is_empty():
                    sample_doc_id_csv = csv_docs.head(1)["docID"].item()
                
                pdf_docs = df_list.filter(pl.col("pdfFlag") == "1")
                if not pdf_docs.is_empty():
                    sample_doc_id_pdf = pdf_docs.head(1)["docID"].item()

            if sample_doc_id_csv is None:
                results.append("注意: CSVフラグが立つdocIDが見つかりませんでした。`get_csv`のテストはスキップされます。")
            if sample_doc_id_pdf is None:
                results.append("注意: PDFフラグが立つdocIDが見つかりませんでした。`get_pdf`のテストはスキップされます。")

        except Exception as e:
            results.append(f"### `client.get_list('{today}')`")
            results.append(f"エラー: {e}")
            sample_doc_id_csv = None # Ensure no further tests if list fails
            sample_doc_id_pdf = None

        # --- get_csv ---
        if sample_doc_id_csv:
            try:
                df_csv = await client.get_csv(sample_doc_id_csv)
                results.append(f"### `client.get_csv('{sample_doc_id_csv}')`")
                results.append(f"CSVデータ (shape: {df_csv.shape}):")
                results.append(mo.as_html(df_csv.head()))
            except Exception as e:
                results.append(f"### `client.get_csv('{sample_doc_id_csv}')`")
                results.append(f"エラー: {e}")
        
        # --- get_pdf ---
        if sample_doc_id_pdf:
            try:
                pdf_content = await client.get_pdf(sample_doc_id_pdf)
                results.append(f"### `client.get_pdf('{sample_doc_id_pdf}')`")
                results.append(f"PDFデータ (bytes length: {len(pdf_content)}). 表示は省略。")
            except Exception as e:
                results.append(f"### `client.get_pdf('{sample_doc_id_pdf}')`")
                results.append(f"エラー: {e}")

    except Exception as e:
        results.append(f"EDINETクライアントの初期化または予期せぬエラー: {e}")
    finally:
        await client.aclose()
    return mo.md("\n".join(results))

async def explore_jquants_apis():
    mo.md("## J-Quants API 探索")
    client = JQuantsClient.create()
    results = []
    try:
        # --- get_info ---
        try:
            df_info = await client.get_info()
            results.append("### `client.get_info()`")
            results.append(f"上場銘柄情報 (shape: {df_info.shape}):")
            results.append(mo.as_html(df_info.head()))
            
            sample_code = None
            if not df_info.is_empty():
                sample_code = df_info.head(1)["Code"].item()
            
            if sample_code is None:
                results.append("注意: 銘柄コードが見つかりませんでした。他のJ-Quants APIのテストはスキップされます。")

        except Exception as e:
            results.append("### `client.get_info()`")
            results.append(f"エラー: {e}")
            sample_code = None

        # --- get_prices ---
        if sample_code:
            try:
                # Fetch prices for a recent date or range
                prices_date = datetime.date(2024, 8, 1) # Example date
                df_prices = await client.get_prices(code=sample_code, date=prices_date)
                results.append(f"### `client.get_prices(code='{sample_code}', date='{prices_date}')`")
                results.append(f"株価データ (shape: {df_prices.shape}):")
                results.append(mo.as_html(df_prices.head()))
            except Exception as e:
                results.append(f"### `client.get_prices(code='{sample_code}', date='{prices_date}')`")
                results.append(f"エラー: {e}")

        # --- get_statements ---
        if sample_code:
            try:
                statements_date = datetime.date(2024, 3, 31) # Example fiscal year end
                df_statements = await client.get_statements(code=sample_code, date=statements_date)
                results.append(f"### `client.get_statements(code='{sample_code}', date='{statements_date}')`")
                results.append(f"財務諸表データ (shape: {df_statements.shape}):")
                results.append(mo.as_html(df_statements.head()))
            except Exception as e:
                results.append(f"### `client.get_statements(code='{sample_code}', date='{statements_date}')`")
                results.append(f"エラー: {e}")

        # --- get_announcement ---
        try:
            df_announcement = await client.get_announcement()
            results.append("### `client.get_announcement()`")
            results.append(f"発表情報データ (shape: {df_announcement.shape}):")
            results.append(mo.as_html(df_announcement.head()))
        except Exception as e:
            results.append("### `client.get_announcement()`")
            results.append(f"エラー: {e}")

        # --- get_trades_spec ---
        try:
            trades_spec_from = datetime.date(2024, 8, 1) # Example date range
            trades_spec_to = datetime.date(2024, 8, 2)
            df_trades_spec = await client.get_trades_spec(from_=trades_spec_from, to=trades_spec_to)
            results.append(f"### `client.get_trades_spec(from_='{trades_spec_from}', to='{trades_spec_to}')`")
            results.append(f"取引仕様データ (shape: {df_trades_spec.shape}):")
            results.append(mo.as_html(df_trades_spec.head()))
        except Exception as e:
            results.append(f"### `client.get_trades_spec(from_='{trades_spec_from}', to='{trades_spec_to}')`")
            results.append(f"エラー: {e}")

    except Exception as e:
        results.append(f"J-Quantsクライアントの初期化または予期せぬエラー: {e}")
    finally:
        await client.aclose()
    return mo.md("\n".join(results))

# Run both explorations
edinet_output = mo.as_html(asyncio.run(explore_edinet_apis()))
jquants_output = mo.as_html(asyncio.run(explore_jquants_apis()))

mo.md(f"{edinet_output}\n{jquants_output}")
