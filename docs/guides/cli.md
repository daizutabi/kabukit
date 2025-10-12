# コマンドラインインターフェースの使い方

kabukit は、[J-Quants API](https://jpx-jquants.com/)
および
[EDINET API](https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html)
からデータを取得するための便利なコマンドラインインターフェース（CLI）を提供します。

コマンド名は `kabu` です。

```console exec="on" source="console" width="80"
$ kabu --help
```

## 認証

### J-Quants API

J-Quants API を利用するには、事前にユーザー登録が必要です。
`auth jquants` サブコマンドを使い、登録したメールアドレスとパスワードで認証して、
ID トークンを取得します。
ID トークンはユーザーの設定ディレクトリに保存されます。

```bash
$ kabu auth jquants
Mailaddress: your_email@example.com
Password: your_password
J-QuantsのIDトークンを保存しました。
```

### EDINET API

EDINET API を利用するには、事前に API キーの取得が必要です。`auth edinet` サブコマンド使い、取得した API キーをユーザーの設定ディレクトリに保存します。

```bash
$ kabu auth edinet
Api key: your_api_key
EDINETのAPIキーを保存しました。
```

### 認証データの確認

認証データの保存先と内容は、`auth show` サブコマンドで確認できます。

```bash
$ kabu auth show
設定ファイル: /home/your_name/.config/kabukit/.env
JQUANTS_ID_TOKEN: ******
EDINET_API_KEY: ******
```

## データ取得

`get` サブコマンドは、J-Quants API および EDINET API から各種データを取得します。

### J-Quants API

#### 上場銘柄一覧

```console exec="on" source="console"
$ kabu get info 7203
```

#### 財務情報

```console exec="on" source="console"
$ kabu get statements 7203
```

#### 株価情報

```console exec="on" source="console"
$ kabu get prices 7203
```

#### 全銘柄のデータ一括取得

各コマンドで銘柄コードを省略すると、全銘柄のデータを一度に取得できます。財務情報の場合は以下の通りです。

```bash
$ kabu get statements
100%|██████████████████████████████| 3787/3787 [01:18<00:00, 48.24it/s]
shape: (165_891, 105)
(略)
```

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
キャッシュディレクトリ '/home/your_name/.cache/kabukit' を正常にクリーンアップしました。
```
