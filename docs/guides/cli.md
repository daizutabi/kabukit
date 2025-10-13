# コマンドラインインターフェースの使い方

kabukit は、[J-Quants API](https://jpx-jquants.com/)
および
[EDINET API](https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html)
からデータを取得するための、
便利なコマンドラインインターフェース（CLI）を提供します。

コマンド名は `kabu` です。

## 認証

### J-Quants API

J-Quants API を利用するには、事前に
[ユーザー登録](https://jpx-jquants.com/auth/signup/?lang=ja)
が必要です。

`auth jquants` サブコマンドを使い、登録したメールアドレスとパスワードで認証して、
ID トークンを取得します。
ID トークンはユーザーの設定ディレクトリに保存されます。

```bash
$ kabu auth jquants
Mailaddress: my_email@example.com
Password: my_password
J-QuantsのIDトークンを保存しました。
```

### EDINET API

EDINET API を利用するには、事前に
[API キーの取得](https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/download/ESE140206.pdf)
が必要です。

`auth edinet` サブコマンド使い、取得した API キーをユーザーの設定ディレクトリに保存します。

```bash
$ kabu auth edinet
Api key: my_api_key
EDINETのAPIキーを保存しました。
```

### 認証データの確認

認証データの保存先と内容は、`auth show` サブコマンドで確認できます。

```bash
$ kabu auth show
設定ファイル: /home/my_name/.config/kabukit/.env
JQUANTS_ID_TOKEN: ******
EDINET_API_KEY: ******
```

## データ取得

`get` サブコマンドは、J-Quants API および EDINET API から各種データを取得します。

### 上場銘柄一覧 (`info`)

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

### 財務情報

`get statements`サブコマンドを使います。

銘柄コードを指定すると、指定した銘柄の財務情報を取得できます。

```console exec="on" source="console"
$ kabu get statements 7203
```

銘柄コードを省略すると、全銘柄の財務情報を一度に取得できます。

```bash
$ kabu get statements
100%|███████████████████████████████████████| 3787/3787 [01:28<00:00, 42.61it/s]
shape: (165_891, 105)
(略)
```

銘柄コードを省略したときに限り、
取得した財務情報はキャッシュディレクトリに自動で保存されます。

### 株価情報

`get prices`サブコマンドを使います。

銘柄コードを指定すると、指定した銘柄の全期間分の株価情報を取得できます。

```console exec="on" source="console"
$ kabu get prices 7203
```

```bash
$ kabu get prices
100%|████████████████████████████████████████████| 3787/3787 [12:33<00:00,  5.02it/s]
shape: (8_128_217, 16)
(略)
```

### 書類一覧

EDINET APIを使い、提出書類の一覧を取得します。
`get entries`サブコマンドを使います。

```bash
$ kabu get entries
100%|██████████████████████████████████████| 3653/3653 [00:42<00:00, 86.47it/s]
shape: (896_632, 30)
(略)
```

### 全銘柄・全データの一括取得

`get all` サブコマンドを使うと、全銘柄の各種データを一度に取得できます。

```bash
$ kabu get all
```

これらのデータはキャッシュディレクトリに保存され、
後でPythonコードから再利用できます。
キャッシュデータを確認するには、`cache tree` サブコマンドを使います。

```console exec="on" source="console"
$ kabu cache tree
```

キャッシュデータは、`cache clean` サブコマンドで消去できます。

```bash
$ kabu cache clean
キャッシュディレクトリ '/home/my_name/.cache/kabukit' を正常にクリーンアップしました。
```

<!-- なお、`limit`キーワードを指定せずに、10 年分の全銘柄の情報を取得するのに
要する時間、および、戻り値の DataFrame の行数は以下のとおりです。

- 10 年分の全銘柄の財務情報：約 70 秒、約 16 万行 -->

<!-- なお、`limit`キーワードを指定せずに、10 年分の全銘柄の株価情報を取得するのに
要する時間、および、戻り値の DataFrame の行数は以下のとおりです。

- 10 年分の全銘柄の株価情報：約 12 分、約 8 百万行 -->
