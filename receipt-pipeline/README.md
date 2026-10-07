# レシート自動取込パイプライン

MEGUMIさんがひつじさんのLINEグループに送った領収書の写真を自動でGCSに保存し（Cloud Function側、`line-webhook-work/`）、このフォルダのスクリプトがGCSから同期→Claudeで読み取り→`現金出納帳_セリエコンチェルト (1).xlsx`へ記帳する。

## 構成

- `ledger.jsonl` — 記帳データの唯一の正（Single Source of Truth）。2026年7月〜10月分（本日手動処理した151枚分 + 入金調整）を初期データとして移行済み
- `excel_builder.py` — `ledger.jsonl` から現金出納帳.xlsx を毎回ゼロから組み立て直す
- `ocr.py` — レシート画像1枚をClaudeに渡して構造化データを抽出
- `gcs_sync.py` — GCSの`receipts/`から新着画像だけをダウンロード（`synced_objects.txt`で二重取得を防止）
- `sync_and_process.py` — 上記を一通り実行する本体（タスクスケジューラから呼ぶのはこれ）
- `migrate_initial_ledger.py` — 一回限りの初期移行スクリプト（実行済み、再実行しない）

## セットアップ手順

### 1. Cloud Function のデプロイ（Phase A）

既存の関数名・リージョンを確認:

```
gcloud functions list --project=<既存のGCPプロジェクトID>
```

同じ関数名・リージョンに対して上書きデプロイ（**新しい関数は作らない＝Webhook URLは変更不要**）:

```
gcloud functions deploy <既存の関数名> ^
  --gen2 ^
  --runtime=python312 ^
  --region=<既存のリージョン> ^
  --source=line-webhook-work ^
  --entry-point=line_webhook ^
  --trigger-http ^
  --allow-unauthenticated ^
  --update-env-vars=RECEIPT_ALLOWED_USER_IDS=,RECEIPT_GROUP_ID=
```

（`--gen2`や既存の環境変数名は、実際の既存デプロイ設定に合わせて調整してください。`gcloud functions describe <関数名>` で現在の設定を確認できます。）

### 2. MEGUMIさんのLINE userId特定（Phase B）

1. 上記デプロイ後、MEGUMIさんにグループへ画像を1枚送ってもらう
2. ログを確認:
   ```
   gcloud functions logs read <関数名> --region=<リージョン> --limit=50
   ```
3. `displayName='MEGUMI'`（またはそれらしい名前）に対応する `userId` と `groupId` をログから見つける
4. 環境変数だけ更新（コード再デプロイ不要）:
   ```
   gcloud functions deploy <関数名> --update-env-vars RECEIPT_ALLOWED_USER_IDS=<userId>,RECEIPT_GROUP_ID=<groupId>
   ```

### 3. ローカル環境のセットアップ

```
pip install -r requirements.txt
gcloud auth application-default login
```

環境変数を設定（PowerShellの例。恒久化するにはシステム環境変数に設定）:

```
setx GCS_BUCKET_NAME "<既存のGCSバケット名>"
setx ANTHROPIC_API_KEY "<Anthropic APIキー>"
```

バケットへの読み取り権限（`Storage Object Viewer`以上）が、ログインしているGoogleアカウントに必要です。

### 4. 動作確認（手動実行）

```
cd C:\Users\user\Desktop\serierepository\receipt-pipeline
python sync_and_process.py
```

`run_log.txt` に実行ログが追記される。新着画像があれば `領収書` フォルダに保存され、Excelが更新される。

### 5. タスクスケジューラ登録（Phase D、1時間おき）

```
schtasks /create /tn "ReceiptSyncAndProcess" /tr "C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe C:\Users\user\Desktop\serierepository\receipt-pipeline\sync_and_process.py" /sc hourly /mo 1 /rl highest
```

## 運用上の注意

- **完全自動記帳**: 人の確認なしでExcelに即時反映される。Claudeの判断に自信が無いもの（金額が斜線・黒塗りで一部読み取れない等）は、店名・摘要欄に `[自動判定・要確認]` と付記されるので、定期的にExcelをざっと見て、おかしい箇所がないか確認することを推奨
- **金額が全く読めない・レシートと判定できない画像**は記帳されず、`run_log.txt` に記録される（画像ファイル自体は `領収書` フォルダに残るので、後で手動確認・手動記帳が可能）
- **Excelを開いたまま**だとその回の再構築はスキップされ、次回実行時に自動的にリトライされる（データは失われない。`ledger.jsonl`への記帳自体は毎回成功する）
- 月をまたいだら(例: 11月分が発生したら)、`excel_builder.py`が自動的に新しいシートを作る。手動での追加作業は不要
