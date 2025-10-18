# キャッシュの活用

CLI の `kabu get` コマンドで取得された各種情報は、
キャッシュとしてローカルストレージに保存されます。
ノートブックなどからは、これらのキャッシュを直接読み込むことができます。
情報取得のためにウェブアクセスが不要になるため、分析をすぐに開始できます。

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

!!! note
    J-Quants API は、データ販売ではなく、データを利用するサービスです。
    取得したデータを蓄積して利用することは許可されていません。不要になった
    キャッシュは削除するようお願いします。
    詳しくは以下に示す J-Quants API の公式 FAQ を参照してください。

    - [サブスクリプションのキャンセルまたは退会後に、データを利用することは可能ですか？](https://jpx.gitbook.io/j-quants-ja/faq/usage#sabusukuripushonnokyanserumatahanidtawosurukotohadesuka)
    - [プラン変更後、変更前のプランのデータを利用することは可能ですか？](https://jpx.gitbook.io/j-quants-ja/faq/usage#purannopurannodtawosurukotohadesuka)
