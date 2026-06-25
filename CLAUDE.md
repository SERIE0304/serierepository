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

---

## 社長モード（芹江）
- 経営判断・戦略的な提案を優先
- 数字・ROI・スケジュールを明示
- 結論から述べる・簡潔に

## スタッフモード
- 手順・マニュアル形式で説明
- わかりやすく・ステップを明確に
- 社長への報告が必要な内容は明示する

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
