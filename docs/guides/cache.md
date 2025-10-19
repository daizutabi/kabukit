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

## キャッシュの保存先

キャッシュディレクトリの場所は、OSによって異なります。
kabukit は [platformdirs](https://platformdirs.readthedocs.io/en/latest/)
ライブラリを使用しており、
各 OS の標準的なディレクトリにキャッシュを保存します。

| OS      | キャッシュディレクトリの場所                           |
| :------ | :------------------------------------------------ |
| Linux   | `~/.cache/kabukit`                                |
| macOS   | `~/Library/Caches/kabukit`                        |
| Windows | `C:\Users\<ユーザー名>\AppData\Local\kabukit\Cache` |

## CLI でのキャッシュ管理

`kabu cache` コマンドを使って、キャッシュの管理ができます。

### ツリー表示 (`tree`)

`kabu cache tree` コマンドを使うと、
キャッシュディレクトリの構造をツリー形式で表示できます。

```console exec="on" source="console" result="ansi"
$ kabu cache tree
```

取得した日付とファイルサイズが表示されます。
不要になったキャッシュは、このツリー表示をもとに手動で削除することもできます。

### 消去 (`clean`)

`kabu cache clean` コマンドを使うと、
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

[`kabukit.cache`][kabukit.core.cache] モジュールは、
Pythonからキャッシュを操作するための関数を提供します。

### 読み込み (`read`)

[`cache.read`][kabukit.core.cache.read] 関数を使って、
キャッシュを読み込めます。
`group` 引数でキャッシュのグループを指定し、
`name` 引数で特定のファイルを指定します。
`name` には拡張子 `.parquet` は含めません。
`name` を省略すると、その `group` の最新のキャッシュファイルが読み込まれます。

まず、現在のキャッシュの状態を確認しておきます。

```console exec="on" source="console" result="ansi"
$ kabu cache tree
```

キャッシュファイル (`*.parquet`) がグループごとにディレクトリに
分割されています。`group` 引数には、このディレクリ名を指定します。
また、最新のキャッシュを使うことが多いので、
ほとんどの場合、`name` 引数は省略されます。

以下では、上場銘柄一覧 ("info") の最新データを読み込み、
最後の 3 行を表示します。

```python exec="1" source="material-block"
from kabukit import cache

cache.read("info").tail(3)
```

### 書き込み (`write`)

[`cache.write`][kabukit.core.cache.write] 関数を使って、
キャッシュを書き込むこともできます。
CLI コマンドでは、実行した日付でファイル名が自動で設定されるのに対し、
Python コードでは、ユーザーがファイル名を指定することができます。

以下では、トヨタ自動車 (銘柄コード 7203) の銘柄情報を `toyota.parquet`
というファイル名で保存します。

```python exec="1" source="material-block" result="1"
from kabukit import get_info

df = await get_info("7203")
cache.write("info", df, "toyota")
```

### 一覧の取得 (`glob`)

[`cache.glob`][kabukit.core.cache.glob] 関数を使って
キャッシュファイルのパス一覧を取得することができます。

引数には`group`を指定します。

```python exec="1" source="material-block" result="1"
for path in cache.glob("info"):
    print(path)
```

ここで、`cache.glob` 関数の戻り値は、ファイルの
更新日時順でソートされています。
先ほど作成した `toyota.parquet` が末尾に追加されていることが分かります。

引数を省略すると、全てのキャッシュファイルのパスを取得できます。

```python exec="1" source="material-block" result="1"
for path in cache.glob():
    print(path)
```

```python .md#_
for path in cache.glob("info"):
    if path.name == "toyota.parquet":
        path.unlink()
```
