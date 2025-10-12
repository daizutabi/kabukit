# はじめに

kabukit は、日本の金融市場データを効率的に取得・解析するための Python ツールキットです。
以下の 2 つの API をサポートしています。

- [J-Quants API](https://jpx-jquants.com/)
- [EDINET API](https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html)

高速なデータ処理ライブラリである [Polars](https://pola.rs/) と、
モダンな非同期 HTTP クライアントである [httpx](https://www.python-httpx.org/)
を基盤として構築されており、パフォーマンスを重視しています。

## インストール

`uv` または `pip` を使ってインストールします。
Python バージョンは 3.12 以上が必要です。

```bash
pip install kabukit
```

## ドキュメントの構成

<!-- このドキュメントは、kabukit の利用方法から、
その背景にある分析コンセプト、データ処理の詳細、
そして具体的な投資分析ワークフローまでを網羅しています。 -->

- 利用ガイド
    - [コマンドラインインターフェースの使い方](guides/cli.md)
    - [J-Quants API の使い方](guides/jquants.md)
    - [EDINET API の使い方](guides/edinet.md)
<!-- - [分析コンセプト](concept/index.md): kabukit の分析哲学と中核となる指標について
- [データレイヤー](data_layer/index.md): データソースの仕様、データ加工・計算ロジックの詳細
- [投資分析ワークフロー](workflow/index.md): kabukit を使った具体的な投資分析の進め方
- [CLIリファレンス](cli_reference.md): コマンドラインインターフェースの詳しい使い方 -->
