---
hide:
  - navigation
---

<style>
  .md-typeset h1,
  .md-content__button {
    display: none;
  }
</style>

<p align="center" style="margin-top: 0px; margin-bottom: 0px;">
  <img src="assets/images/logo.svg">
</p>

<p align="center" style="margin-top: 0px; margin-bottom: 0px;">
  <img src="assets/images/kabukit.svg">
</p>

# はじめに

<p align="center" style="margin-bottom: 40px;">
日本の株式投資分析を、もっと手軽に、もっと速く
</p>

**kabukit** は、J-Quants と EDINET のデータを、
コマンドラインや Python コードから快適に扱うための
モダンなツールキットです。

## なぜ kabukit なのか？

日本株の投資分析には、様々なデータソースへのアクセスが必要です。
しかし、それぞれの API は仕様が異なり、データ取得だけで多くの時間を費やしてしまいます。
kabukit は、こうした課題を解決します。

<div class="grid cards" markdown>

- **:fontawesome-solid-terminal: ターミナルから即座にデータ取得**

    ---

    API の認証設定が対話形式で簡単に完了。
    `kabu get prices` の一行で、全上場銘柄の 10 年分[^1] の株価データが手に入り、
    すぐに分析を始められます。

- **:fontawesome-solid-code: ノートブックで快適な分析体験**

    ---

    `await get_statements()` と書くだけで、全上場銘柄の財務情報を非同期で並列取得。
    [Polars](https://pola.rs/) によるデータフレーム操作で、数千銘柄のデータも瞬時に処理できます。

- **:fontawesome-solid-database: 賢いキャッシュで高速アクセス**

    ---

    一度取得したデータはローカルに保存され、次回からは瞬時にアクセス可能。
    ネットワークアクセスを待つことなく、何度でも試行錯誤できます。

- **:fontawesome-solid-rocket: モダンな技術スタックで高速処理**

    ---

    [httpx](https://www.python-httpx.org/) の非同期処理により、複数銘柄のデータを並列取得。
    従来の同期的なアプローチと比べ、データ取得時間を大幅に短縮します。

</div>

[^1]: J-Quants API スタンダードプラン利用時。詳しくは、[J-Quants API](https://jpx-jquants.com/)
      のプラン表を参照してください。

## クイックスタート

=== "pip でインストール"

    ```bash
    pip install kabukit
    ```

=== "uv でインストール"

    ```bash
    uv add kabukit
    ```

インストールしたら、まずは認証設定から始めましょう。

```bash
# J-Quants API の認証（対話形式）
kabu auth jquants

# 上場銘柄一覧を取得
kabu get info

# トヨタ自動車の財務情報を取得
kabu get statements 7203
```

つぎに、Python コードから使ってみましょう。

```python
from kabukit import get_info, get_prices

# 上場銘柄一覧を取得
df_info = await get_info()

# トヨタ自動車の株価を取得
df_prices = await get_prices("7203")
```

!!! note
    [Jupyter](https://jupyter.org/) や [marimo](https://marimo.io/)
    などのノートブック環境では、`await` 式を直接記述できます。

## 主な機能

### :material-api: 2つの API を統一的に扱える

- **[J-Quants API](https://jpx-jquants.com/)**: 上場銘柄情報、財務情報、株価四本値など
- **[EDINET API](https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html)**: 有価証券報告書などの開示書類

異なる API の仕様差を吸収し、同じインターフェースで利用できます。

### :material-flash: 高速なデータ処理

- **[Polars](https://pola.rs/)**: Rust ベースの高速データフレームライブラリ
- **[httpx](https://www.python-httpx.org/)**: 非同期 HTTP クライアントによる並列データ取得
- **キャッシュ機構**: 取得済みデータの再利用で、分析の試行錯誤を高速化

### :material-tools: 柔軟な利用方法

- **CLI**: スクリプト不要で、ターミナルから直接データ取得
- **Python API**: ノートブック環境での対話的な分析に最適
- **キャッシュ活用**: CLI で取得したデータを Python から読み込み可能

## 次のステップ

kabukit の使い方を、以下のガイドで詳しく解説しています。

- **[CLIの使い方](guides/cli.md)**:
  認証設定から、データ取得、キャッシュ管理まで、
  コマンドラインインターフェース (CLI) の全機能を解説

- **[J-Quants API の使い方](guides/jquants.md)**:
  上場銘柄情報、財務情報、株価四本値を、Python から取得する方法。
  モジュール関数と `JQuantsClient` の使い分け

- **[EDINET API の使い方](guides/edinet.md)**:
  有価証券報告書などの開示書類を、Python から取得する方法。
  モジュール関数と `EdinetClient` の使い分け

- **[キャッシュの活用](guides/cache.md)**:
  キャッシュの仕組みと、CLI および Python からの管理方法
