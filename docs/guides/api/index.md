# Python API の使い方

kabukit は、複数のソースからデータを取得するための、
Python API 提供します。

現在サポートしているソースは以下の通りです。

- [J-Quants API](https://jpx-jquants.com/)
- [EDINET API](https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html)
- [TDnet](https://www.release.tdnet.info/inbs/I_main_00.html)

## ノートブックで非同期処理

kabukit は、[httpx](https://www.python-httpx.org/) を使った非同期設計になっており、
[Jupyter](https://jupyter.org/) や [marimo](https://marimo.io/) のような
非同期処理を直接扱えるノートブック環境で快適に利用できます。

## 2 つのインターフェース

Python API は、モジュール関数と Client クラスの 2 のインターフェースを提供します。

### モジュールレベル関数

httpx クライアントを意識することなく、手軽にデータを取得にするのに
適しています。また、銘柄コードや日付を複数指定すると、関数内部で非同期処理を
並列実行するため、効率的に情報を取得できます。

### Client クラス

より詳細な制御（例: タイムアウト設定、リトライポリシーの変更など）
が必要な場合に直接利用します。
特に、各クラスの `client` 属性は `httpx.AsyncClient` のインスタンスであるため、
httpx が提供する豊富なメソッドや設定に直接アクセスすることが可能です。
