"""
営業訪問用資料を生成するスクリプト。
候補地リスト(panda_sales_candidates.txt)を読み込み、
各エリア向けの営業トークシート + 会社紹介資料をMarkdownで出力する。
"""

import env_loader
import os, json, anthropic
from datetime import datetime

client = anthropic.Anthropic()

COMPANY_INFO = """
【会社情報】
会社名：株式会社芹江コンチェルト
所在地：栃木県那須塩原市（JR黒磯駅近く）
代表者：芹江（セリエ）
事業内容：
  - 旅館業 Lodgers Bldg SERIE
  - パンダベビーカステラ（キッチンカー・物産展）
  - Honey LaRva フィットネスボクシングジム（大田原市・那須塩原市）

【パンダベビーカステラについて】
商品：ベビーカステラ（パンダ型）
特徴：
  - 見た目がかわいいパンダ型でSNS映え抜群
  - 焼きたてアツアツで子どもから大人まで人気
  - 栃木県那須塩原市発のご当地スイーツ
  - キッチンカー・物産展どちらにも対応
価格帯：500円〜（袋サイズにより異なる）
出店実績：栃木県内各所のイベント・物産展

【出店条件（当社から提供）】
- キッチンカー：駐車スペース1台分（約3m×6m）
- 電源：100V 15A以上（なければ発電機対応可）
- 水道：できれば近くにあると助かりますが、タンク持参可
- 出店費用：売上歩合制 or 固定出店料（要相談）
- 営業時間：10:00〜17:00が標準（応相談）
- 必要な許可：食品営業許可取得済み、保健所届出済み
"""

PROMPT = """あなたはパンダベビーカステラ（栃木県那須塩原市のキッチンカー）の営業担当です。

以下の会社・商品情報をもとに、施設・イベント主催者向けの「営業訪問資料」を日本語で作成してください。

{company_info}

---
【候補地リスト（調査結果）】
{candidates}
---

以下の構成でMarkdown形式の営業資料を作成してください：

# パンダベビーカステラ 出店のご提案

## 1. 商品紹介
（パンダベビーカステラの魅力を3〜4行で）

## 2. 出店のメリット（相手へのメリット）
（施設・イベント主催者にとってのメリットを箇条書き5点）

## 3. 出店条件・スペック
（必要なスペース・電源・費用形態をわかりやすく）

## 4. 出店実績・信頼性
（実績・食品営業許可などの信頼ポイント）

## 5. エリア別 営業アプローチメモ
候補地リストをもとに、各エリア（那須塩原市/大田原市/那須町/白河市）ごとに：
  - 最優先候補（施設名・担当者へのトークポイント）
  - 電話でのセールストーク例（1〜2行）
  - 訪問時の持参物チェックリスト

## 6. 問い合わせ・連絡先
（会社名・電話・メール等のテンプレ）

---
読み手：施設の担当者・イベント主催者
トーン：丁寧でポジティブ、数字や具体例を使う
文字数：制限なし（実用的な分量で）
"""

def load_candidates():
    path = os.path.join(os.path.dirname(__file__), 'panda_sales_candidates.txt')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return '（候補地リストがまだありません。先に panda_local_research.py を実行してください）'

def main():
    today = datetime.now().strftime('%Y/%m/%d')
    print('パンダ🐼営業資料生成中...')

    candidates = load_candidates()
    prompt = PROMPT.replace('{company_info}', COMPANY_INFO).replace('{candidates}', candidates)

    result = client.messages.create(
        model='claude-sonnet-4-5',
        max_tokens=4000,
        messages=[{'role': 'user', 'content': prompt}]
    )

    doc = ''
    for block in result.content:
        if hasattr(block, 'text'):
            doc += block.text

    # Markdownファイルとして保存
    out_path = os.path.join(os.path.dirname(__file__), f'panda_sales_sheet_{today.replace("/", "")}.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f'# パンダベビーカステラ 営業資料\n生成日: {today}\n\n')
        f.write(doc)

    print(f'\n===== 営業資料 =====\n')
    print(doc)
    print(f'\n資料保存先: {out_path}')

if __name__ == '__main__':
    main()
