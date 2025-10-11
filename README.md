# kabukit

A Python toolkit for Japanese financial market data, supporting J-Quants and EDINET APIs.

[![PyPI Version][pypi-v-image]][pypi-v-link]
[![Python Version][python-v-image]][python-v-link]
[![Build Status][GHAction-image]][GHAction-link]
[![Coverage Status][codecov-image]][codecov-link]
[![Documentation Status][docs-image]][docs-link]

kabukitは、高速なデータ処理ライブラリである [Polars](https://pola.rs/) と、モダンな非同期HTTPクライアントである [httpx](https://www.python-httpx.org/) を基盤として構築されており、パフォーマンスを重視しています。

## インストール

`uv` または `pip` を使って、[Python Package Index (PyPI)](https://pypi.org/) からインストールします。Pythonバージョンは3.13以上が必要です。

```bash
uv pip install kabukit
```

## コマンドラインから使う

kabukitは、 [J-Quants](https://jpx-jquants.com/) および [EDINET](https://disclosure2.edinet-fsa.go.jp/) からデータを取得するための便利なコマンドラインインターフェース（CLI）を提供します。

コマンド名は `kabu` です。

### 認証

#### J-Quants

J-Quants APIを利用するにはユーザー登録が必要です。`auth jquants` サブコマンドを使い、登録したメールアドレスとパスワードで認証し、IDトークンを取得します。IDトークンはユーザーの設定ディレクトリに保存されます。

```bash
❯ kabu auth jquants
Mailaddress: your_email@example.com
Password: your_password
J-QuantsのIDトークンを保存しました。
```

#### EDINET

EDINET APIを利用するには、事前にAPIキーの取得が必要です。取得したAPIキーを `auth edinet` サブコマンドで保存します。

```bash
❯ kabu auth edinet
Api key: your_api_key
EDINETのAPIキーを保存しました。
```

#### 認証データで確認

認証データの保存先と内容は、`auth show` サブコマンドで確認できます。

```bash
❯ kabu auth show
Configuration file: /home/your_name/.config/kabukit/.env
JQUANTS_ID_TOKEN: ******
EDINET_API_KEY: ******
```

### データ取得

`get` サブコマンドは、J-QuantsおよびEDINETから各種データを取得します。以下に、一例を示します。

#### 銘柄情報

```bash
❯ kabu get info 7203
shape: (1, 8)
┌────────────┬───────┬──────────────┬──────────────────┬─
│ Date       ┆ Code  ┆ CompanyName  ┆ Sector17CodeName ┆
│ ---        ┆ ---   ┆ ---          ┆ ---              ┆
│ date       ┆ str   ┆ str          ┆ cat              ┆
╞════════════╪═══════╪══════════════╪══════════════════╪═
│ 2025-10-14 ┆ 72030 ┆ トヨタ自動車 ┆ 自動車・輸送機   ┆
└────────────┴───────┴──────────────┴──────────────────┴─
```

#### 財務情報

```bash
❯ kabu get statements 7203
shape: (41, 105)
(略)
```

#### 株価情報

```bash
❯ kabu get prices 7203
shape: (2_444, 16)
(略)
```

#### 全銘柄のデータ一括取得

各コマンドで銘柄コードを省力すると、全銘柄のデータを一度に取得できます。財務情報の場合は以下の通りです。

```bash
> kabu get statements
100%|█████████████████████████████████████| 3787/3787 [01:18<00:00, 48.24it/s]
shape: (165_891, 105)
(略)
```

`get all` サブコマンドを使うと、全銘柄の各種データを一度に取得できます。

```bash
> kabu get all
```

これらのデータはキャッシュディレクトリに保存され、後で再利用できます。キャッシュデータを確認するには、`cache tree` サブコマンドを使います。

```bash
> kabu cache tree
/home/your_name/.cache/kabukit
├── info
│   └── 20251011.parquet
├── list
│   └── 20251011.parquet
├── prices
│   └── 20251011.parquet
├── reports
│   └── 20251011.parquet
└── statements
    └── 20251011.parquet
```

キャッシュデータは、`cache clean` サブコマンドで消去できます。


## ノートブックから使う

`kabukit`はPythonモジュールとしてAPIを提供します。[Jupyter](https://jupyter.org/) や [marimo](https://marimo.io/) のノートブックから使用できます。

### データ取得

J-Quantsの例を示します。まず、`JQuantsClient`のインスタンスを作成します。事前に、コマンドラインで認証を済ませてください。

```python
from kabukit import JQuantsClient

client = JQuantsClient()
```

#### 銘柄情報

```python
info = await client.get_info("7203")
```

#### 財務情報

```python
statements = await client.get_statements("7203")
```

#### 株価情報

```python
prices = await client.get_prices("7203")
```

#### 全銘柄のデータ一括取得

`fetch_all`関数を使うと、全銘柄のデータを一度に取得できます。marimoノートブックを使っていてば、プログレスバーを簡単に表示できます。財務情報の場合は以下の通りです。

```python
import marimo as mo
from kabukit.jquants import fetch_all

statements = await fetch_all("statements", progress=mo.status.progress_bar)
```

株価情報の場合は、上記の `"statements"` を `"prices"` に変更してください。

### キャッシュデータの利用

コマンドラインで事前に保存しておいたキャッシュデータを再利用できます。ノートブックの起動ごとに、APIアクセスを行ってデータをダウンロードする必要がなくなります。

```python
from kabukit import Info, Statements, Prices

# data属性で、Polars DataFrameを取得できます。
info = Info.read().data
statements = Statements.read().data
prices = Prices.read().data
```

<!-- Badges -->

[pypi-v-image]: https://img.shields.io/pypi/v/kabukit.svg
[pypi-v-link]: https://pypi.org/project/kabukit/
[python-v-image]: https://img.shields.io/pypi/pyversions/kabukit.svg
[python-v-link]: https://pypi.org/project/kabukit
[GHAction-image]: https://github.com/daizutabi/kabukit/actions/workflows/ci.yaml/badge.svg?branch=main&event=push
[GHAction-link]: https://github.com/daizutabi/kabukit/actions?query=event%3Apush+branch%3Amain
[codecov-image]: https://codecov.io/github/daizutabi/kabukit/graph/badge.svg?token=Yu6lAdVVnd
[codecov-link]: https://codecov.io/github/daizutabi/kabukit?branch=main
[docs-image]: https://img.shields.io/badge/docs-latest-blue.svg
[docs-link]: https://daizutabi.github.io/kabukit/