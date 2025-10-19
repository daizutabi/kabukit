<p align="center">
  <img src="https://raw.githubusercontent.com/daizutabi/kabukit/main/docs/assets/images/logo.svg" alt="Kabukit Logo" style="width: 3cm;">
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/daizutabi/kabukit/main/docs/assets/images/kabukit.svg" alt="Kabukit" style="width: 5cm;">
</p>

<p align="center">
  <em>A Python toolkit for Japanese financial market data, supporting J-Quants and EDINET APIs.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/kabukit/"><img src="https://img.shields.io/pypi/v/kabukit.svg"/></a>
  <a href="https://pypi.org/project/kabukit/"><img src="https://img.shields.io/pypi/pyversions/kabukit.svg"/></a>
  <a href="https://github.com/daizutabi/kabukit/actions?query=event%3Apush+branch%3Amain"><img src="https://github.com/daizutabi/kabukit/actions/workflows/code-quality-tests.yaml/badge.svg?branch=main&event=push"/></a>
  <a href="https://codecov.io/github/daizutabi/kabukit?branch=main"><img src="https://codecov.io/github/daizutabi/kabukit/graph/badge.svg?token=Yu6lAdVVnd"/></a>
  <a href="https://daizutabi.github.io/kabukit/"><img src="https://img.shields.io/badge/docs-latest-blue.svg"/></a>
</p>

**kabukit** は、 [J-Quants API](https://jpx-jquants.com/) および [EDINET API](https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html) から、効率的に日本の金融市場データを取得するツールキットです。

高速なデータ処理ライブラリである [Polars](https://pola.rs/) と、モダンな非同期 HTTP クライアントである [httpx](https://www.python-httpx.org/) を基盤として構築されており、パフォーマンスを重視しています。

## インストール

`pip` または `uv` を使ってインストールします。Python バージョンは 3.12 以上が必要です。

```bash
pip install kabukit
```

## コマンドラインから使う

kabukit は、 [J-Quants API](https://jpx-jquants.com/) および [EDINET API](https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html) からデータを取得するための便利なコマンドラインインターフェース（CLI）を提供します。

具体的な使い方は、次の利用ガイドを参照してください。

- [コマンドラインインターフェースの使い方](https://daizutabi.github.io/kabukit/guides/cli/)

## ノートブックから使う

kabukit は、コマンドラインだけでなく、Python コードからも API として利用できます。httpx を使って非同期でデータを取得するため、[Jupyter](https://jupyter.org/) や [marimo](https://marimo.io/) のような非同期処理を直接扱えるノートブック環境と非常に相性が良いです。

具体的な使い方は、以下の利用ガイドを参照してください。

- [J-Quants API の使い方](https://daizutabi.github.io/kabukit/guides/jquants/)
- [EDINET API の使い方](https://daizutabi.github.io/kabukit/guides/edinet/)
