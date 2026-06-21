# 株式会社芹江コンチェルト — エージェントチーム

## 会社概要

**株式会社芹江コンチェルト**（栃木県那須塩原市・JR黒磯駅近く）

| 事業 | 概要 |
|------|------|
| Lodgers Bldg SERIE | 旅館業（黒磯駅徒歩圏） OTA: Booking.com / Airbnb / VRBO |
| パンダベビーカステラ | キッチンカー・物産展。パンダ型ベビーカステラ |
| Honey LaRva | フィットネスボクシングジム（大田原市・那須塩原市 直営2店舗） |

---

## エージェント一覧（cron スケジュール）

| # | エージェント | ファイル | スケジュール（WSL cron） | 使用モデル |
|---|------------|---------|----------------------|-----------|
| 1 | SERIE料金レポート | pricing_agent.py | 毎週月曜 8:00 | Sonnet 4-6 + Haiku 4-5 |
| 2 | パンダ販路レポート | panda_agent.py | 毎週月曜 8:00 | Sonnet 4-5 + Haiku 4-5 |
| 3 | 補助金レポート | hojyokin_agent.py | 毎週月曜 8:00 | Sonnet 4-5 + Haiku 4-5 |
| 4 | Honey LaRva集客 | larva_agent.py | 毎週月曜 8:00 | Sonnet 4-5 + Haiku 4-5 |
| 5 | 不動産調査 | fudosan_agent.py | 毎週月曜 8:00 | Sonnet 4-5 + Haiku 4-5 |
| 6 | ボクシングSNS台本 | sns_agent.py | 毎日 8:00 / 12:00 / 18:00 | Opus 4-5 + Haiku 4-5 |
| 7 | 予約確認通知 | booking_checker.py | 毎朝 7:00 | Google Calendar API（LLMなし） |
| 8 | FC化レポート | fc_agent.py | 月初の月曜 8:00 | Haiku 4-5 |
| 9 | タスク週次レビュー | task_manager.py | 毎週金曜 8:00 | LINE直送（LLMなし） |
| 10 | パンダ地域営業調査 | panda_local_research.py | **手動実行** | Sonnet 4-5（web検索） |
| 11 | パンダ営業資料生成 | panda_sales_sheet.py | **手動実行** | Sonnet 4-5 |

---

## 各エージェント詳細

### 1. SERIE料金レポート（pricing_agent.py）

- **目的**: 黒磯駅周辺の競合施設料金を調査し、今週・来週のSERIE推奨料金を算出
- **LINEヘッダー**: `【SERIE料金レポート】YYYY/MM/DD`
- **調査内容**: 那須塩原市中央町3-12から近い順に施設3件 + エリアイベント情報
- **出力**: 300文字以内。平日/土日の推奨価格・理由・今週のアクション1つ

### 2. パンダ販路レポート（panda_agent.py）

- **目的**: 東京エリアのキッチンカー出店募集・マルシェ・物産展の情報を収集
- **LINEヘッダー**: `【パンダカステラ販路レポート】YYYY/MM/DD`
- **調査エリア**: 東京（代々木公園・吉祥寺・二子玉川）、栃木物産展（銀座matsuri等）
- **出力**: 600文字以内。イベント名・日時・申込URL・締切・今週すぐ申込めるアクション1つ

### 3. 補助金レポート（hojyokin_agent.py）

- **目的**: 3事業（SERIE・パンダ・Honey LaRva）が対象になる補助金を優先度別に整理
- **LINEヘッダー**: `【補助金レポート】YYYY/MM/DD`
- **調査内容**: 那須塩原市・栃木県・国の公募中補助金を「緊急/今月中/次回公募待ち」に分類
- **出力**: 600文字以内。ですます調・絵文字使用・今週のアクション1つ

### 4. Honey LaRva集客レポート（larva_agent.py）

- **目的**: ジムの会員獲得と自治体連携機会を調査
- **LINEヘッダー**: `【Honey LaRvaレポート】YYYY/MM/DD`
- **調査内容**: 自治体健康増進事業連携 / 法人契約（ベネフィットワン等） / 地域スポーツイベント / 最新集客トレンド
- **出力**: 600文字以内。ですます調・絵文字使用・今週のアクション1つ

### 5. 不動産調査レポート（fudosan_agent.py）

- **目的**: 那須塩原市の売買物件情報と地価指標を調査
- **LINEヘッダー**: `【不動産レポート】YYYY/MM/DD`
- **調査内容**:
  - 黒磯駅・那須塩原駅それぞれ半径1km以内の売買物件（2000万円以内）
  - 旅館業・飲食・フィットネス転用可能物件を優先
  - 公示地価・基準地価・路線価・実勢価格の4指標と買い時判定
- **出力**: 600文字以内。ですます調・絵文字使用・今週のアクション1つ

### 6. ボクシングSNS台本（sns_agent.py）

- **目的**: 最新ボクシングニュースを検索し、YouTube【芹江案件チャンネル】用台本を生成
- **LINEヘッダー**: `[boxing news] YYYY/MM/DD HH:MM`
- **調査内容**: 直近48時間の試合結果・日本人ファイター・世界タイトルマッチ・計量問題を優先
- **台本構成**: ①掴み30秒 ②解説1分 ③元チャンプ視点3分 ④Honey LaRva絡み1.5分 ⑤クロージング30秒
- **特記**: ニュースなし時は「NO_NEWS_TODAY」を返してLINE送信をスキップ

### 7. 予約確認通知（booking_checker.py）

- **目的**: Google Calendar から7日間の予約を取得し、OTA別に分類してLINE送信
- **LINEヘッダー**: `【SERIE予約確認】YYYY/MM/DD`
- **OTA検出と絵文字**:
  - 🔵 Booking.com（"booking.com" / "booking"）
  - 🔴 Airbnb（"airbnb" / "エアビー"）
  - 🟢 VRBO（"vrbo" / "homeaway" / "ホームアウェイ"）
  - ⚪ Direct（上記以外）
- **出力例**: チェックイン〜チェックアウト（X泊）を各OTAブロックで表示
- **LLM**: 使用しない（正規表現でOTA判定）

### 8. FC化レポート（fc_agent.py）

- **目的**: Honey LaRvaのフランチャイズ化に向けた月次進捗調査
- **LINEヘッダー**: `【FC化レポート】YYYY/MM/DD`
- **調査内容**: FC本部要件・準備事項（マニュアル/収益モデル/研修）・費用目安・成功事例・相談窓口（栃木県よろず支援拠点等）
- **スケジュール**: 月初の月曜のみ実行（中長期戦略レポート）

### 9. タスク週次レビュー（task_manager.py）

- **目的**: `tasks.json` に蓄積されたタスクを毎週金曜にまとめてLINE通知
- **LINEヘッダー**: 未完了/完了タスクのサマリー
- **依存ファイル**: `~/lodgers/agents/tasks.json`
- **LLM**: 使用しない（JSON読み書きのみ）

### 10. パンダ地域営業調査（panda_local_research.py）

- **目的**: 4エリアの出店候補地をウェブ検索で調査し、LINE送信 + ファイル保存
- **調査エリア**: 那須塩原市 / 大田原市 / 那須町 / 福島県白河市
- **候補地タイプ**: 道の駅・定期マルシェ・スーパー駐車場イベント・観光施設・物産展
- **出力**: `panda_sales_candidates.txt` を上書き更新。優先度★★★/★★/★で評価
- **LINEヘッダー**: `【パンダ🐼営業候補地リスト】YYYY/MM/DD`

### 11. パンダ営業資料生成（panda_sales_sheet.py）

- **目的**: `panda_sales_candidates.txt` を読み込み、施設担当者向け営業資料をMarkdown生成
- **入力**: `panda_sales_candidates.txt`（panda_local_research.pyの出力）
- **出力**: `panda_sales_sheet_YYYYMMDD.md`
- **資料構成**: 商品紹介 / 出店メリット / スペック表 / 実績 / エリア別トークスクリプト / 連絡先テンプレ / 週次営業スケジュール

---

## 環境設定

### APIキー読込（env_loader.py）

```
読込優先順:
1. 環境変数 ANTHROPIC_API_KEY が既にセットされていれば何もしない
2. ~/.env
3. ~/lodgers/.env
```

### LINE Messaging API（get_line_token.py）

- Channel ID: `2010176953`
- 実行時に動的トークン取得（`/v2/oauth/accessToken`）
- **LINE_USER_ID**: `U206a030c1759f1ed8f4c684d03d11915`

### Google Calendar（booking_checker.py 専用）

```
requirements.txt に記載のライブラリを使用:
  google-auth, google-auth-oauthlib, google-auth-httplib2, google-api-python-client
```

### タスク管理（tasks.json）

```json
{
  "tasks": [
    {
      "category": "カテゴリ名",
      "task": "タスク内容",
      "done": false,
      "added": "YYYY/MM/DD",
      "week": "YYYY-Www"
    }
  ]
}
```

---

## 手動実行コマンド（WSL）

```bash
cd ~/lodgers/agents

python pricing_agent.py          # SERIE料金レポート → LINE
python panda_agent.py            # パンダ東京販路レポート → LINE
python panda_local_research.py   # パンダ地域営業候補地調査 → LINE + panda_sales_candidates.txt
python panda_sales_sheet.py      # 営業訪問資料生成 → panda_sales_sheet_YYYYMMDD.md
python hojyokin_agent.py         # 補助金レポート → LINE
python larva_agent.py            # Honey LaRva集客レポート → LINE
python fudosan_agent.py          # 不動産レポート → LINE
python sns_agent.py              # ボクシングSNS台本 → LINE
python booking_checker.py        # 予約確認 → LINE
python fc_agent.py               # FC化レポート → LINE
python task_manager.py           # タスク週次レビュー → LINE
```

---

## 生成ファイル

| ファイル | 生成元 | 内容 |
|---------|--------|------|
| `panda_sales_candidates.txt` | panda_local_research.py | 4エリア出店候補地リスト（実行のたびに上書き） |
| `panda_sales_sheet_YYYYMMDD.md` | panda_sales_sheet.py | 施設担当者向け営業訪問資料 |
| `tasks.json` | task_manager.py / 各エージェント | 週次タスク蓄積 |
| `*.log` | cron実行ログ | panda.log / sns.log / fudosan.log / hojyokin.log / larva.log |

---

## リポジトリ

- **GitHub**: `serie0304/serierepository`
- **作業ブランチ（agentsチーム）**: `claude/business-overview-lc99a2`
- **作業ブランチ（quiz_app）**: `claude/upbeat-bardeen-ds1j09`
