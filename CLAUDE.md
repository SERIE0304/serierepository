# 芹江コンチェルト - Claude Code 設定

## ★ セッション開始時に必ずすること

**毎回セッションの一番最初に、必ず以下を聞いてください：**

> 「芹江さんですか？それともスタッフの方ですか？お名前を教えてください。」

回答を受け取ったら、すぐに以下のコマンドで記録してください：

```bash
cd /home/user/serierepository/agents && python -c "
from activity_logger import log_activity
log_activity('【名前】', 'セッション開始', 'Claude Codeセッション')
"
```
（【名前】の部分は実際の名前に置き換える）

名前を受け取ったら、**必ず以下のエージェント一覧を表示してください：**

---

【現在のエージェントと仕事一覧】

📦 panda_agent.py　→　パンダベビーカステラ 販路調査
　　東京のキッチンカー出店募集・マルシェ情報を検索してレポートを作成。
　　小筆さんはこのレポートを印刷して営業先に持参できます。

💰 hojyokin_agent.py　→　補助金調査
　　SERIE・パンダ・LaRva の3事業向け補助金を緊急度別に整理。
　　申請期限が近いものを優先して一覧化します。

🏠 fudosan_agent.py　→　不動産調査
　　那須塩原・黒磯エリアの売買物件情報と地価動向を調査。
　　2000万円以内・駅近の物件に絞ってレポートします。

🥊 larva_agent.py　→　Honey LaRva 集客調査
　　自治体連携・法人契約・地域イベントへの出展チャンスを調査。
　　週1回のアクションを提案します。

🏨 pricing_agent.py　→　SERIE 料金提案
　　競合ホテルの料金を調べて、SERIEの今週・来週の推奨料金を提案。
　　イベント需要も考慮した価格設定をします。

📱 sns_agent.py　→　SNS・YouTube台本生成
　　最新ボクシングニュースを収集してYouTube台本を自動生成。
　　芹江さんの顔出しトーク用に仕上げます。

🏢 fc_agent.py　→　Honey LaRva FC化調査
　　フランチャイズ化の手順・費用・スケジュールを調査。
　　法的要件から専門家への相談先まで整理します。

📅 booking_checker.py　→　SERIE 予約確認
　　GoogleカレンダーからSERIEの今後7日間の予約を取得して表示。

---

実行方法：`cd /home/user/serierepository/agents && python 【agent名】`
資料の確認：Leidy チャット → http://localhost:5000/reports

---

## 社長モード（芹江）
- 経営判断・戦略的な提案を優先
- 数字・ROI・スケジュールを明示
- 結論から述べる・簡潔に

## スタッフモード（小筆）
- 手順・マニュアル形式で説明
- わかりやすく・ステップを明確に
- 社長への報告が必要な内容は明示する

## スタッフ一覧
- 小筆

---

## 会社情報
- **会社名**: 株式会社芹江コンチェルト（栃木県那須塩原市黒磯）
- **事業①**: Lodgers Bldg SERIE（旅館業・Booking.com/Airbnb/VRBO）
- **事業②**: Honey LaRva（フィットネスボクシングジム・大田原市・那須塩原市）
- **事業③**: パンダベビーカステラ（移動販売）
- **社長**: 芹江匡晋（元プロボクシング日本スーパーバンタム級35代チャンピオン）

## エージェント一覧（agents/）
- `leidy_chat.py` - ブラウザチャット（localhost:5000）
- `hojyokin_agent.py` - 補助金調査
- `fudosan_agent.py` - 不動産調査
- `panda_agent.py` - パンダカステラ販路
- `larva_agent.py` - Honey LaRva集客
- `sns_agent.py` - SNS・YouTube台本
- `activity_logger.py` - 活動ログ（`python activity_logger.py` で確認）
