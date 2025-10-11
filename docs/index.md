# はじめに

`kabukit`は、日本の金融市場データ、特にJ-QuantsおよびEDINET APIから取得したデータを効率的に扱うためのPythonツールキットです。

kabukitは、高速なデータ処理ライブラリである [Polars](https://pola.rs/) と、モダンな非同期HTTPクライアントである [httpx](https://www.python-httpx.org/) を基盤として構築されており、パフォーマンスを重視しています。

## インストール

`uv` または `pip` を使って、[Python Package Index (PyPI)](https://pypi.org/) からインストールします。Pythonバージョンは3.13以上が必要です。

```bash
uv pip install kabukit
```

## ドキュメントの構成

このドキュメントは、`kabukit`の利用方法から、その背景にある分析コンセプト、データ処理の詳細、そして具体的な投資分析ワークフローまでを網羅しています。

*   [分析コンセプト](concept/index.md): `kabukit`の分析哲学と中核となる指標について。
*   [データレイヤー](data_layer/index.md): データソースの仕様、データ加工・計算ロジックの詳細。
*   [投資分析ワークフロー](workflow/index.md): `kabukit`を使った具体的な投資分析の進め方。
<!-- *   [CLIの使用方法](cli/index.md): コマンドラインインターフェースの詳しい使い方。
*   [ノートブックの例](notebooks/index.md): ノートブックを使った実践的な利用例。 -->
