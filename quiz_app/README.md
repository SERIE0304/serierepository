# 社内研修クイズアプリ

スタッフ向けに業務オペレーションの問題を出題し、自動採点・成績集計を行う無料のWebアプリです。
データはGoogleスプレッドシートに保存されます。

## できること
- 「実務編」「フランチャイジー編」の2つの編に分けて問題を作成・出題
- スタッフが名前・編・カテゴリを選んでクイズに回答 → 自動採点 → 結果と解説を表示
- 管理者ダッシュボードで編ごとにスタッフ別ランキング・カテゴリ別正答率を確認
- 管理者画面から編・カテゴリを指定して問題の追加・削除

## セットアップ

### 1. 依存パッケージのインストール
```
cd quiz_app
pip install -r requirements.txt
```

### 2. Googleスプレッドシートの準備
1. Google Cloud Consoleでサービスアカウントを作成し、JSONキーをダウンロードして
   `quiz_app/credentials.json` として保存する（リポジトリの `.gitignore` で除外済み）。
2. Google Sheets API を有効化する。
3. 保存用のスプレッドシートを新規作成し、そのスプレッドシートをサービスアカウントの
   メールアドレス（credentials.jsonの`client_email`）に編集者として共有する。
4. スプレッドシートのURLからIDを取得する（`/d/` と `/edit` の間の文字列）。

シート（Questions・Responses）は初回起動時に自動で作成されます。

### 3. 環境変数の設定
```
export QUIZ_SPREADSHEET_ID="あなたのスプレッドシートID"
export GOOGLE_CREDENTIALS_PATH="credentials.json"   # 省略時はquiz_app直下のcredentials.json
export ADMIN_PASSWORD="好きな管理者パスワード"
export QUIZ_QUESTION_COUNT="10"   # 1回のクイズで出題する問題数（省略時は10）
export FLASK_SECRET_KEY="任意のランダム文字列"
```

### 4. 起動
```
python app.py
```
`http://localhost:5000` にアクセスします。管理者画面は `/admin` から（要パスワード）。

## 無料での運用について
- ローカルPCや社内サーバーで動かせばサーバー費用は無料です。
- 外部公開したい場合は Render / Railway / Fly.io などの無料枠でデプロイできます。
- データ保存はGoogleスプレッドシートのみなので追加のデータベース費用は不要です。
