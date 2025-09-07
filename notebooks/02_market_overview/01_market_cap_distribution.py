import marimo as mo
import polars as pl
import plotly.express as px
import asyncio

from kabukit.jquants.client import JQuantsClient

# --- J-Quants API Key Setup Reminder ---
# Before running this notebook, ensure your J-Quants API keys are set up.
# You can do this by running the 'auth' method of JQuantsClient
# or by setting JQUANTS_REFRESH_TOKEN and JQUANTS_ID_TOKEN
# environment variables.
# For example, in a Python script or another notebook:
# import asyncio
# from kabukit.jquants.client import JQuantsClient
# async def setup_jquants_auth():
#     client = JQuantsClient.create()
#     try:
#         await client.auth(mailaddress="YOUR_EMAIL", password="YOUR_PASSWORD")
#         print("J-Quants authentication successful!")
#     except Exception as e:
#         print(f"J-Quants authentication failed: {e}")
#     finally:
#         await client.aclose()
# asyncio.run(setup_jquants_auth())
# --------------------------------------

async def fetch_jquants_data():
    client = JQuantsClient.create()
    try:
        # Get listed stock information
        # This might contain market capitalization or data to derive it
        listed_info_df = await client.get_info()
        return listed_info_df
    except Exception as e:
        return mo.md(f"**Error fetching J-Quants data:** {e}")
    finally:
        await client.aclose()

# Run the async function to fetch data
listed_info = mo.as_html(asyncio.run(fetch_jquants_data()))

# Display the head of the DataFrame to inspect columns
# You will need to run this Marimo notebook to see the output
# and determine how to calculate market capitalization.
mo.md(
    f"""
# 01. 時価総額分布の分析

J-Quantsから取得した上場銘柄情報です。
時価総額の計算に必要なカラム（例: 発行済み株式数、株価）を確認してください。

{listed_info}
"""
)
