# SERIE プロジェクト - 前提知識

## ブランド：パンダカステラ

### ブランドストーリー
上野のパンダの思い出 → 那須への恩返しコンセプト

### 素材（3点）
- 那須御養卵
- 千本松牧場の牛乳
- 栃木産米粉

### 出店実績（6件）
- 東武百貨店 大田原店
- 東武百貨店 宇都宮店
- ソラマチ
- 渋谷
- 江東区
- 高輪ゲートウェイ

### 現在の取引先
- トコトコ大田原
- 道の駅 那須の与一の郷

### 出店形態
- キッチンカー・マルシェ出店
- 物産展への参加

---

## 別事業：Lodgers Bldg SERIE（民泊）

- 場所：栃木県那須塩原市（JR黒磯駅近く）
- 現在料金：6,000円/泊
- OTA：Booking.com、Airbnb、VRBO

---

## エージェントチーム（agents/）

| ファイル | 役割 |
|---|---|
| panda_agent.py | パンダカステラ販路調査・LINE通知 |
| sns_agent.py | SNS投稿 |
| pricing_agent.py | 民泊料金提案 |
| booking_checker.py | 予約確認 |
| fudosan_agent.py | 不動産情報 |
| hojyokin_agent.py | 補助金情報 |
| larva_agent.py | その他エージェント |
| task_manager.py | タスク管理 |
| webhook_server.py | Webhookサーバー |

## 通知
- LINE Bot経由でレポートを受信
