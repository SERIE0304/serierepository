import env_loader
import os, json, anthropic
from datetime import datetime

client = anthropic.Anthropic()

DIR = os.path.dirname(os.path.abspath(__file__))
CANDIDATES_FILE = os.path.join(DIR, 'panda_sales_candidates.txt')

COMPANY_INFO = """
【会社情報】
会社名：株式会社芹江コンチェルト
所在地：栃木県那須塩原市（JR黒磯駅近く）
事業：旅館業 Lodgers Bldg SERIE / なんだパンダベビーカステラ / Honey LaRva フィットネスボクシングジム（大田原市・那須塩原市 直営2店舗）

【なんだパンダベビーカステラ】
ブランドストーリー：
  2018年、東京（妻：上野稲荷町 / 夫：門前仲町）から栃木県大田原市へ移住。子供2人。
  妻が子供たちを連れて上野動物園のパンダを見に行っていた思い出から、
  那須地方での「パンダ型カステラ × 地産地消素材」というコンセプトが生まれ、
  「東京と那須への恩返し」として誕生したブランド。

商品の特徴：
  - 形状：パンダ型
  - 食感：モチっとしてカリッとする独特の食感
  - 粉：国産米粉 100%使用（小麦粉不使用）
  - 卵：那須御養卵
  - 牛乳：千本松牧場の牛乳
  - 賞味期限：当日限り（焼きたて・無添加）

出店実績：大田原東武百貨店、宇都宮東武百貨店、東京ソラマチ、渋谷キャストガーデン、東京江東区民祭り、高輪ゲートウェイ
現在の定期取引先：トコトコ大田原（大田原市）、道の駅・那須の与一の郷（大田原市）、道の駅・明治の森黒磯（那須塩原市）

出店スペック：
  - 必要スペース：約3m×6m（キッチンカー1台分）
  - 電源：100V・15A以上（延長コード持参可）
  - 水道：タンク持参で対応可
  - 出店費用：売上歩合制または固定出店料（要相談）
  - 標準営業時間：10:00〜17:00
  - 許認可：食品営業許可取得済み・移動販売届出済み
"""

PROMPT = """あなたはなんだパンダベビーカステラの営業担当です。
今日は{today}です。

以下の会社・商品情報と候補地リストをもとに、施設担当者に手渡しできる
「営業提案資料」をMarkdown形式で作成してください。

{company_info}

---
【営業候補地リスト（調査済み）】
{candidates}
---

以下の構成で作成してください：

# なんだパンダベビーカステラ 出店のご提案
生成日：{today}

## はじめに — ブランドストーリー
（2018年東京からの移住、上野動物園のパンダへの思い出、那須地方への恩返しの想いを温かく3〜4行で）

## 商品紹介
（パンダ型・モチカリ食感・100%米粉・那須産素材・当日賞味期限のポイントをわかりやすく）

## 出店スペック一覧
（表形式：スペース・電源・費用形態・営業時間・許認可）

## 出店実績
（表形式：場所・種別）

---

## 営業候補地 提案書

候補地リストにある施設それぞれについて、以下のセクションを作成してください（既存取引先は除外）：

### 【提案】施設名（エリア）
#### この施設となんだパンダベビーカステラが合う理由
（施設の特徴とパンダカステラの強みを照らし合わせて箇条書き3〜4点）
#### 施設へのご提案メッセージ
（担当者に手渡す1段落の提案文）
#### セールストーク例
（電話・訪問時に使える自然な日本語の台本 2〜3行）
#### 問い合わせ先
（電話番号・URL等、候補地リストから転記）

---

## 営業スケジュール（{today}以降の平日）
（翌週月曜から各施設に電話する順番を表形式で。{today}が日曜なので翌日{next_monday}から）

## 訪問時の持参物チェックリスト
（チェックボックス形式）

## 問い合わせ先テンプレート
（施設担当者に渡す連絡先カード形式）

---
トーン：丁寧・ポジティブ・具体的な数字や実績を使う
注意：既存取引先（トコトコ大田原・道の駅那須の与一の郷・道の駅明治の森黒磯）は提案対象から除外
"""

def get_next_monday(today_str):
    from datetime import datetime, timedelta
    d = datetime.strptime(today_str, '%Y/%m/%d')
    days_ahead = 7 - d.weekday() if d.weekday() != 6 else 1
    return (d + timedelta(days=days_ahead)).strftime('%Y/%m/%d')

def load_candidates():
    if not os.path.exists(CANDIDATES_FILE):
        raise FileNotFoundError(
            f'候補地リストが見つかりません: {CANDIDATES_FILE}\n'
            'まず panda_local_research.py を実行してください。'
        )
    with open(CANDIDATES_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    today = datetime.now().strftime('%Y/%m/%d')
    next_monday = get_next_monday(today)
    print('パンダ🐼提案書生成中...')

    candidates = load_candidates()
    prompt = (PROMPT
              .replace('{today}', today)
              .replace('{next_monday}', next_monday)
              .replace('{company_info}', COMPANY_INFO)
              .replace('{candidates}', candidates))

    result = client.messages.create(
        model='claude-sonnet-4-5',
        max_tokens=4000,
        messages=[{'role': 'user', 'content': prompt}]
    )

    doc = ''.join(block.text for block in result.content if hasattr(block, 'text'))

    out_path = os.path.join(DIR, f'panda_sales_proposal_{today.replace("/", "")}.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(doc)

    print(f'提案書生成完了: {out_path}')
    return out_path

if __name__ == '__main__':
    main()
