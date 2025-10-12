# コマンドラインインターフェースの使い方

kabukit は、[J-Quants API](https://jpx-jquants.com/)
および
[EDINET API](https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html)
からデータを取得するための便利なコマンドラインインターフェース（CLI）を提供します。

コマンド名は `kabu` です。

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
J-Quants の ID トークンを保存しました。
```

### EDINET API

EDINET API を利用するには、事前に API キーの取得が必要です。`auth edinet` サブコマンド使い、取得した API キーをユーザーの設定ディレクトリに保存します。

```bash
$ kabu auth edinet
Api key: your_api_key
EDINET の API キーを保存しました。
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

```bash
$ kabu get info 7203
shape: (1, 8)
┌────────────┬───────┬──────────────┬──────────────────┬─
│ Date       ┆ Code  ┆ CompanyName  ┆ Sector17CodeName ┆
│ ---        ┆ ---   ┆ ---          ┆ ---              ┆
│ date       ┆ str   ┆ str          ┆ cat              ┆
╞════════════╪═══════╪══════════════╪══════════════════╪═
│ 2025-10-14 ┆ 72030 ┆ トヨタ自動車   ┆ 自動車・輸送機     ┆
└────────────┴───────┴──────────────┴──────────────────┴─
```

#### 財務情報

```bash
❯ kabu get statements 7203
shape: (41, 105)
(略)
```

#### 株価情報

```bash
❯ kabu get prices 7203
shape: (2_444, 16)
(略)
```

#### 全銘柄のデータ一括取得

各コマンドで銘柄コードを省略すると、全銘柄のデータを一度に取得できます。財務情報の場合は以下の通りです。

```bash
> kabu get statements
100%|███████████████████████████| 3787/3787 [01:18<00:00, 48.24it/s]
shape: (165_891, 105)
(略)
```

`get all` サブコマンドを使うと、全銘柄の各種データを一度に取得できます。

```bash
> kabu get all
```

これらのデータはキャッシュディレクトリに保存され、後で再利用できます。キャッシュデータを確認するには、`cache tree` サブコマンドを使います。

```bash
> kabu cache tree
/home/your_name/.cache/kabukit
├── info
│   └── 20251011.parquet (63.8 KB)
├── list
│   └── 20251011.parquet (10.2 MB)
├── prices
│   └── 20251011.parquet (175.7 MB)
├── reports
│   └── 20251011.parquet (713.4 KB)
└── statements
    └── 20251011.parquet (12.5 MB)
```

キャッシュデータは、`cache clean` サブコマンドで消去できます。
