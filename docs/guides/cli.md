# CLI の使い方

kabukit は、[J-Quants API](https://jpx-jquants.com/)
および
[EDINET API](https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html)
からデータを取得するための、
便利なコマンドラインインターフェース（CLI）を提供します。

コマンド名は `kabu` です。このコマンドの役割は大きく分けて 3 つあります。

1. J-Quants API および EDINET API の認証情報を設定します。
   これにより、ノートブックなどで使うときに、認証について気にする必要が
   なくなります。
2. 各コマンドで銘柄コードや日付を引数に与えることで、最小限の
   ネットワークアクセスで各 API から情報を取得します。結果はすぐにターミナル
   に表示されるので、API との通信が正常であること、および、取得した情報が
   期待通りであることを迅速に確認できます。
3. 銘柄コードや日付を省略することで、
   非同期並列通信を活かして多量の情報を取得できます。
   取得した情報は、キャッシュディレクトリに保存されます。
   このキャッシュデータを使うことで、
   ノートブックなどで、分析をすぐに始められます。

以下のガイドでは、これらの特徴を順次説明していきます。

## 認証設定 (`auth`)

`kabu auth` コマンドは、以下の優先順位で認証情報を探索します。

1. コマンドラインオプション (例: `--mailaddress`)
2. 設定ファイル (例: `~/.config/kabukit/config.toml`)
3. 環境変数 (例: `JQUANTS_MAILADDRESS`)
4. 上記いずれにも見つからない場合は、インタラクティブな入力プロンプトを表示

### J-Quants API (`jquants`)

J-Quants API を利用するには、事前に
[ユーザー登録](https://jpx-jquants.com/auth/signup/?lang=ja)
が必要です。

`kabu auth jquants` コマンドで、
事前登録したメールアドレスとパスワードを使って認証を行い、
ID トークンを取得します。
取得した ID トークンは、設定ファイルに保存され、
あとから再利用されます。

#### 対話的な使い方

オプションを指定せずにコマンドを実行すると、メールアドレスとパスワードの入力を求められます。

```bash
$ kabu auth jquants
Mailaddress: my_email@example.com
Password:
J-QuantsのIDトークンを保存しました。
```

#### 非対話的な使い方

CI/CD 環境など、対話的な入力ができないときは、
コマンドラインオプションまたは環境変数で認証情報を指定できます。

- コマンドラインオプション

```bash
$ kabu auth jquants --mailaddress my_email@example.com --password my_password
```

- 環境変数

```bash
$ export JQUANTS_MAILADDRESS="my_email@example.com"
$ export JQUANTS_PASSWORD="my_password"
$ kabu auth jquants
```

### EDINET API (`edinet`)

EDINET API を利用するには、事前に
[API キーの取得](https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/download/ESE140206.pdf)
が必要です。

`kabu auth edinet` コマンドで API キーを設定ファイルに保存します。

#### 対話的な使い方

```bash
$ kabu auth edinet
Api key: my_api_key
EDINETのAPIキーを保存しました。
```

#### 非対話的な使い方

- コマンドラインオプション

```bash
$ kabu auth edinet --api-key my_api_key
```

- 環境変数

```bash
$ export EDINET_API_KEY="my_api_key"
```

!!! note
    環境変数を設定しているときは、別途
    `kabu auth edinet`コマンドを実行する
    必要はありません。

### 認証設定の表示 (`show`)

認証設定の保存先と内容は、`kabu auth show` コマンドで表示できます。

```bash
$ kabu auth show
設定ファイル: /home/my_name/.config/kabukit/config.toml
JQUANTS_ID_TOKEN = "..."
EDINET_API_KEY = "..."
```

## 情報取得 (`get`)

`kabu get` コマンドは、J-Quants API および EDINET API から各種情報を取得します。

### 上場銘柄一覧 (`info`)

`kabu get info` コマンドを使うと、
J-Quants API から上場銘柄一覧を取得します。

銘柄コード (4桁) を指定すると、指定した銘柄の最新情報を取得できます。

```console exec="on" source="console"
$ kabu get info 7203
```

日付 (YYYYMMDD) を指定すると、指定した日時もしくは
直近の営業日における全銘柄の最新情報を取得できます。

```console exec="on" source="console"
$ kabu get info 20230101
```

銘柄コードを省略すると、全銘柄の最新情報を一度に取得できます。

```console exec="on" source="console"
$ kabu get info
```

- `--quiet` または `-q` オプションを付けると、取得したデータフレームの表示を抑制できます。

銘柄コードを指定したときは、表示されたデータフレームはどこにも保存されずに
プログラムは終了します。
単純に J-Quants API へのリクエストが正常に処理され、期待通りの情報が得られていることを
確認したいケースで用います。

一方、銘柄コードを省略したときは、
取得した上場銘柄一覧はキャッシュディレクトリに保存されます。
このキャッシュデータを使うことで、
ノートブックなどで、分析をすぐに始められます。

この仕様は、以下で説明する他のコマンドでも共通です。

### 財務情報 (`statements`)

`kabu get statements` コマンドを使うと、
J-Quants API から財務情報を取得します。

銘柄コードを指定すると、指定した銘柄の全期間分の財務情報を取得できます。

```console exec="on" source="console"
$ kabu get statements 7203
```

銘柄コードを省略すると、全銘柄の全期間分の財務情報を一度に取得できます。

```bash
$ kabu get statements
100%|█████████████████████████████████████| 3787/3787 [01:28<00:00, 42.61it/s]
shape: (165_891, 105)
(略)
```

このようにプログレスバーが表示され、進捗状況が把握できるようになっています。
加えて以下のオプションが設定可能です。

- `--quiet` または `-q` オプションを付けると、プログレスバーおよび
  取得したデータフレームの表示を抑制できます。
- `--max-items` オプションを付けると、全銘柄取得時の銘柄数の上限を指定できます。

上の出力例から、次のことがわかります。

- 1 秒間に 40 銘柄程度の財務情報を取得しました。
- トータルで 1 分 30 秒程度かかりました。
- 取得したデータフレームの行数は約 16 万行です。

### 株価情報 (`prices`)

`kabu get prices` コマンドを使うと、
J-Quants API から株価情報を取得します。

銘柄コードを指定すると、指定した銘柄の全期間分の株価情報を取得できます。

```console exec="on" source="console"
$ kabu get prices 7203
```

銘柄コードを省略すると、全銘柄の全期間分の株価情報を一度に取得できます。

```bash
$ kabu get prices
100%|█████████████████████████████████████| 3787/3787 [12:33<00:00,  5.02it/s]
shape: (8_128_217, 16)
(略)
```

このようにプログレスバーが表示され、進捗状況が把握できるようになっています。
加えて以下のオプションが設定可能です。

- `--quiet` または `-q` オプションを付けると、プログレスバーおよび
  取得したデータフレームの表示を抑制できます。
- `--max-items` オプションを付けると、全銘柄取得時の銘柄数の上限を指定できます。

上の出力例から、次のことがわかります。

- 1 秒間に 5 銘柄程度の株価情報を取得しました。
- トータルで 13 分程度かかりました。
- 取得したデータフレームの行数は約 8 百万行です。

### J-Quants 情報の一括取得 (`jquants`)

これまで、J-Quantsが提供する 3 つの情報を、個別のコマンドで取得してきました。
`kabu get jquants` コマンドを使うと、全ての入手可能な情報を一度に取得できます。

```bash
$ kabu get jquants [code]
```

- `code` 引数で銘柄コードを指定すると、その銘柄に関する情報のみを取得します。
- `--quiet` または `-q` オプションを付けると、取得したデータフレームの表示を抑制できます。
- `--max-items` オプションを付けると、全銘柄取得時の銘柄数（または日付数）の上限を指定できます。

銘柄コードを省略したときに限り、
これらの情報はキャッシュディレクトリに保存されます。

### EDINET 書類一覧 (`edinet`)

`kabu get edinet` コマンドを使うと、
EDINET API から提出書類一覧を取得します。

日付 (YYYY-MM-DD) を指定すると、
指定した日付に提出された書類一覧を取得できます。

```console exec="on" source="console"
$ kabu get edinet 2025-10-10
```

日付を省略すると、過去10年分の書類一覧を一度に取得できます。

```bash
$ kabu get edinet
100%|█████████████████████████████████████| 3653/3653 [00:42<00:00, 86.47it/s]
shape: (896_632, 30)
(略)
```

このようにプログレスバーが表示され、進捗状況が把握できるようになっています。
加えて以下のオプションが設定可能です。

- `--quiet` または `-q` オプションを付けると、プログレスバーおよび
  取得したデータフレームの表示を抑制できます。
- `--max-items` オプションを付けると、全期間取得時の日付数の上限を指定できます。

上の出力例から、次のことがわかります。

- 1 秒間に 80 日程度の書類一覧を取得しました。
- トータルで 50 秒程度かかりました。
- 取得したデータフレームの行数は約 90 万行です。

## キャッシュ (`cache`)

これまでに説明したように、
銘柄コードや日付を省略することで、
キャッシュディレクトリに取得した情報が保存されます。

`kabu cache` コマンドを使うと以下のことができます。

- `kabu cache tree`: キャッシュの内容をツリー表示します
- `kabu cache clean`: キャッシュ全体を消去します

キャッシュの仕組みや、Python からの活用方法については、
[キャッシュの活用](cache.md)ガイドを参照してください。
