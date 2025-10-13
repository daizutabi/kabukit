# キャッシュデータの活用

<!-- CLI の `kabu get` コマンドで取得・保存されたデータは、
キャッシュとしてローカルストレージに保存されています。
ノートブックからは、これらのキャッシュデータを直接読み込むことができます。
J-Quants API へのウェブアクセスが不要になるため、分析をすぐに開始できます。

```python
from kabukit import Info, Statements, Prices

# CLI で取得したキャッシュを読み込む
# .data 属性で Polars DataFrame にアクセスできる
info_df = Info.read().data
statements_df = Statements.read().data
prices_df = Prices.read().data
``` -->
