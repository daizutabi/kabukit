# キャッシュの活用

CLI の `kabu get` コマンドで取得された各種情報は、
キャッシュとしてローカルストレージに保存されます。
ノートブックなどからは、これらのキャッシュを直接読み込むことができます。

## キャッシュの目的とメリット

- **APIリクエストの削減**: 同じデータを何度も取得する際に、
  API への不要なリクエストを減らし、利用制限に達するリスクを低減します。
- **高速なデータアクセス**: ローカルストレージから直接データを読み込むため、
  ネットワーク経由での取得よりも格段に速くデータにアクセスできます。
- **オフラインでの利用**: 一度キャッシュされたデータは、オフライン環境でも利用可能です。

## キャッシュの仕組み

キャッシュディレクトリの場所は、OSによって異なります。
kabukit は [platformdirs](https://platformdirs.readthedocs.io/en/latest/) ライブラリを使用しており、
各OSの標準的なディレクトリにキャッシュを保存します。

| OS      | キャッシュディレクトリの場所                           |
| :------ | :------------------------------------------------ |
| Linux   | `~/.cache/kabukit`                                |
| macOS   | `~/Library/Caches/kabukit`                        |
| Windows | `C:\Users\<ユーザー名>\AppData\Local\kabukit\Cache` |

## CLIでのキャッシュ管理

`kabu cache` コマンドを使って、キャッシュの管理ができます。

### ツリー表示 (`tree`)

`cache tree` サブコマンドを使うと、
キャッシュディレクトリの構造をツリー形式で表示できます。

```console exec="on" source="console"
$ kabu cache tree
```

取得した日付とファイルサイズが表示されます。
不要になったキャッシュは、このツリー表示をもとに手動で削除することもできます。

### 消去 (`clean`)

`cache clean` サブコマンドを使うと、
キャッシュ情報をすべて消去できます。

```bash
$ kabu cache clean
キャッシュディレクトリ '/home/my_name/.cache/kabukit' を正常にクリーンアップしました。
```

!!! warning
    `cache clean` コマンドを実行すると、ユーザーの意思を確認することなく、
    キャッシュがすべて消去されます。ご注意ください。

!!! info
    J-Quants API は、データ販売ではなく、データを利用するサービスです。
    取得したデータを蓄積して利用することは許可されていません。不要になった
    キャッシュは削除するようお願いします。
    詳しくは以下に示す J-Quants API の公式 FAQ を参照してください。

    - [サブスクリプションのキャンセルまたは退会後に、データを利用することは可能ですか？](https://jpx.gitbook.io/j-quants-ja/faq/usage#sabusukuripushonnokyanserumatahanidtawosurukotohadesuka)
    - [プラン変更後、変更前のプランのデータを利用することは可能ですか？](https://jpx.gitbook.io/j-quants-ja/faq/usage#purannopurannodtawosurukotohadesuka)

## Pythonでのキャッシュ利用

まず、現在のキャッシュの状態を確認しておきます。

```console exec="on" source="console"
$ kabu cache tree
```

[`kabukit.core.cache`][] モジュールは、Pythonからキャッシュを操作するための関数を提供します。
なお、`cache`モジュールは、`kabukit` パッケージから公開されているので、

```python exec="1" source="material-block"
from kabukit import cache
```

のようにインポートできます。

### キャッシュの読み込み (`cache.read`)

[`kabukit.core.cache.read`][] 関数を使って簡単に読み込めます。
`group` 引数でキャッシュのカテゴリ（例: "prices", "info"）を指定し、
`name` 引数で特定のファイル名を指定します。`name` を省略すると、
その `group` の最新のファイルが読み込まれます。

```python exec="1" source="material-block"
cache.read("info").tail(3)
```

### キャッシュの書き込み (`cache.write`)

[`kabukit.core.cache.write`][] 関数を使って
キャッシュを書き込むこともできます。

```python exec="1" source="material-block"
from kabukit import get_info

df = await get_info("7203")
cache.write("info", df, "7203")
```

### キャッシュリスト (`cache.glob`)

[`kabukit.core.cache.glob`][] 関数を使って
キャッシュの一覧を取得することができます。

```python exec="1" source="material-block"
list(cache.glob("info"))
```

### キャッシュの削除 (`cache.glob`)
<!-- ```python
import polars as pl
from kabukit.core import cache

# 株価情報を読み込む (最新のファイル)
prices_df = cache.read(group="prices")
print(prices_df.head())

# 特定のファイル名を指定して読み込む (例: "20240701" 部分)
specific_prices_df = cache.read(group="prices", name="20240701")
print(specific_prices_df.head())
```

#### データの書き込み (`cache.write`)

`kabukit.core.cache.write` 関数を使って、DataFrameをキャッシュに保存できます。
`group` 引数でキャッシュのカテゴリを指定し、`name` 引数でファイル名を指定します。`name` を省略すると、現在の日付がファイル名として使用されます。

```python
import polars as pl
from kabukit.core import cache

# サンプルデータ
data_to_cache = pl.DataFrame({"col1": [1, 2], "col2": ["A", "B"]})

# 日付をファイル名として保存
cache.write(group="my_data", df=data_to_cache)

# 特定のファイル名を指定して保存
cache.write(group="my_data", df=data_to_cache, name="custom_data_set")
```

#### キャッシュの消去 (`cache.clean`)

`kabukit.core.cache.clean` 関数を使って、キャッシュを削除できます。
`group` 引数を省略するとキャッシュディレクトリ全体が削除され、`group` を指定するとそのカテゴリのキャッシュのみが削除されます。

```python
from kabukit.core import cache

# キャッシュ全体を削除
cache.clean()

# 特定のグループのキャッシュのみを削除
cache.clean(group="prices") -->
