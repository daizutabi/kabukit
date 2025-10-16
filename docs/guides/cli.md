# コマンドラインインターフェースの使い方

kabukit は、[J-Quants API](https://jpx-jquants.com/)
および
[EDINET API](https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html)
からデータを取得するための、
便利なコマンドラインインターフェース（CLI）を提供します。

コマンド名は `kabu` です。

## 認証

`kabu auth` コマンドは、以下の優先順位で認証情報を探索します。

1. コマンドラインオプション (例: `--mailaddress`)
2. 設定ファイル (例: `~/.config/kabukit/config.toml`)
3. 環境変数 (例: `JQUANTS_MAILADDRESS`)
4. 上記いずれにも見つからない場合は、インタラクティブな入力プロンプトを表示

### J-Quants API

J-Quants API を利用するには、事前に
[ユーザー登録](https://jpx-jquants.com/auth/signup/?lang=ja)
が必要です。

`auth jquants` サブコマンド (エイリアス: `auth j`) で
ID トークンを取得し、設定ファイルに保存します。

#### 基本的な使い方（インタラクティブ）

オプションを指定せずにコマンドを実行すると、対話形式でメールアドレスとパスワードを尋ねられます。

```bash
$ kabu auth jquants
Mailaddress: my_email@example.com
Password:
J-QuantsのIDトークンを保存しました。
```

#### 非インタラクティブな使い方

CI/CD 環境など、対話的な入力ができない場合は、
コマンドラインオプションまたは環境変数で認証情報を指定できます。

- コマンドラインオプションを使う場合

```bash
$ kabu auth jquants --mailaddress my_email@example.com --password my_password
```

- 環境変数を使う場合

```bash
$ export JQUANTS_MAILADDRESS="my_email@example.com"
$ export JQUANTS_PASSWORD="my_password"
$ kabu auth jquants
```

### EDINET API

EDINET API を利用するには、事前に
[API キーの取得](https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/download/ESE140206.pdf)
が必要です。

`auth edinet` サブコマンド (エイリアス: `auth e`) で API キーを
設定ファイルに保存します。

#### 基本的な使い方（インタラクティブ）

```bash
$ kabu auth edinet
Api key: my_api_key
EDINETのAPIキーを保存しました。
```

ただし、すでに設定ファイルや環境変数で API キーが設定されている場合は、
何もしません。

#### 非インタラクティブな使い方

- コマンドラインオプションを使う場合

```bash
$ kabu auth edinet --api-key my_api_key
```

**環境変数を使う場合:**

```bash
$ export EDINET_API_KEY="my_api_key"
$ kabu auth edinet
```

### 認証データの確認

認証データの保存先と内容は、`auth show` サブコマンドで確認できます。

```bash
$ kabu auth show
設定ファイル: /home/my_name/.config/kabukit/config.toml
JQUANTS_ID_TOKEN = "..."
EDINET_API_KEY = "..."
```

## データ取得

`get` サブコマンドは、J-Quants API および EDINET API から各種データを取得します。

### 上場銘柄一覧 (`info`)

J-Quants API を使い、上場銘柄一覧を取得します。
`get info`サブコマンドを使います。

銘柄コードを指定すると、指定した銘柄の最新情報を取得できます。

```console exec="on" source="console"
$ kabu get info 7203
```

銘柄コードを省略すると、全銘柄の最新情報を一度に取得できます。

```console exec="on" source="console"
$ kabu get info
```

銘柄コードを省略したときに限り、
取得した上場銘柄一覧はキャッシュディレクトリに自動で保存されます。

### 財務情報 (`statements`)

J-Quants API を使い、財務情報を取得します。
`get statements`サブコマンドを使います。

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
以下のことがわかります。

- 1秒間に40銘柄程度の財務情報を取得しました。
- トータルで1分30秒程度かかりました。
- 取得したデータフレームの行数は約16万行です。

銘柄コードを省略したときに限り、
取得した財務情報はキャッシュディレクトリに自動で保存されます。

### 株価情報 (`prices`)

J-Quants API を使い、株価情報を取得します。
`get prices`サブコマンドを使います。

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
以下のことがわかります。

- 1秒間に5銘柄程度の株価情報を取得しました。
- トータルで13分程度かかりました。
- 取得したデータフレームの行数は約8百万行です。

銘柄コードを省略したときに限り、
取得した株価情報はキャッシュディレクトリに自動で保存されます。

### 書類一覧 (`entries`)

EDINET APIを使い、提出書類一覧を取得します。
`get entries`サブコマンドを使います。

日付 (YYYY-MM-DD) を指定すると、
指定した日付に提出された書類一覧を取得できます。

```console exec="on" source="console"
$ kabu get entries 2025-10-10
```

日付を省略すると、全銘柄の全期間分の書類一覧を一度に取得できます。

```bash
$ kabu get entries
100%|█████████████████████████████████████| 3653/3653 [00:42<00:00, 86.47it/s]
shape: (896_632, 30)
(略)
```

このようにプログレスバーが表示され、進捗状況が把握できるようになっています。
以下のことがわかります。

- 1秒間に80日程度の書類一覧を取得しました。
- トータルで50秒程度かかりました。
- 取得したデータフレームの行数は約90万行です。

日付を省略したときに限り、
取得した書類一覧はキャッシュディレクトリに自動で保存されます。

### 全データの一括取得 (`all`)

これまで、4 つの情報を個別のコマンドで取得してきました。
`get all` サブコマンドを使うと、全ての入手可能なデータを一度に取得できます。

```bash
$ kabu get all
```

これらのデータはキャッシュディレクトリに保存され、
後で Python コードから再利用できます。
キャッシュデータを確認するには、`cache tree` サブコマンドを使います。

```console exec="on" source="console"
$ kabu cache tree
```

キャッシュデータは、`cache clean` サブコマンドで消去できます。

```bash
$ kabu cache clean
キャッシュディレクトリ '/home/my_name/.cache/kabukit' を正常にクリーンアップしました。
```
