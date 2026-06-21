import env_loader
import os, json, anthropic
from datetime import datetime

client = anthropic.Anthropic()
from get_line_token import get_line_token
LINE_CHANNEL_TOKEN = get_line_token()
LINE_USER_ID = 'U206a030c1759f1ed8f4c684d03d11915'

def send_line_message(message):
    import urllib.request
    data = json.dumps({'to': LINE_USER_ID, 'messages': [{'type': 'text', 'text': message}]}).encode('utf-8')
    req = urllib.request.Request('https://api.line.me/v2/bot/message/push', data=data,
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + LINE_CHANNEL_TOKEN})
    urllib.request.urlopen(req)

AREAS = [
    ('那須塩原市', ['那須塩原市 道の駅 キッチンカー 出店', '那須塩原市 マルシェ イベント 出店者募集', '那須塩原市 スーパー 商業施設 駐車場 キッチンカー 募集']),
    ('大田原市',   ['大田原市 道の駅 キッチンカー 出店', '大田原市 マルシェ フリーマーケット 出店', '大田原市 商店街 イベント キッチンカー 募集']),
    ('那須町',     ['那須町 道の駅 キッチンカー 出店', '那須高原 マルシェ イベント 出店者募集', '那須町 観光施設 物販 出店']),
    ('福島県白河市', ['白河市 道の駅 キッチンカー 出店', '白河市 マルシェ イベント 出店者募集', '白河市 商業施設 イベントスペース キッチンカー']),
]

PROMPT = """今日は{today}です。
あなたはパンダベビーカステラ（栃木県那須塩原市のキッチンカー）の営業担当です。

以下のエリアで出店・販売できる具体的な場所をウェブ検索して調査してください。

調査エリアとキーワード：
{area_keywords}

各エリアについて以下を調べてください：
1. 道の駅・SA・PAなど常設の出店スペースがある施設
2. 定期マルシェ・週末市場・朝市
3. ショッピングセンター・スーパーの駐車場イベントスペース
4. 観光施設・道の駅の催事スペース
5. 地域の物産展・フリーマーケット開催場所

各候補について：
- 施設名・場所（住所）
- 出店形態（常設/定期/不定期）
- 問い合わせ先（電話・HP・担当部署）
- 出店条件（わかれば：費用・必要スペース・電源有無）

出力形式：
【パンダ🐼営業候補地リスト】{today}

エリアごとに箇条書きで整理し、営業優先度（★★★高/★★中/★低）もつけること。
合計1200文字以内。最後に「今週すぐ電話すべき1番の候補」を明記すること。

禁止：「問い合わせが必要です」「確認してください」だけの回答。必ず具体的な施設名と連絡先を記載すること。"""

def build_area_keywords_text():
    lines = []
    for area, keywords in AREAS:
        lines.append(f'【{area}】')
        for kw in keywords:
            lines.append(f'  - {kw}')
    return '\n'.join(lines)

def main():
    today = datetime.now().strftime('%Y/%m/%d')
    print('パンダ🐼地域営業調査エージェント実行中...')

    prompt = PROMPT.replace('{today}', today).replace('{area_keywords}', build_area_keywords_text())

    result = client.messages.create(
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        model='claude-sonnet-4-5',
        max_tokens=2000,
        messages=[{'role': 'user', 'content': prompt}]
    )

    report = ''
    for block in result.content:
        if hasattr(block, 'text'):
            report += block.text

    print(report)
    send_line_message(report)
    print('LINE送信完了！')

    # 結果をファイルにも保存
    out_path = os.path.join(os.path.dirname(__file__), 'panda_sales_candidates.txt')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f'生成日時: {today}\n\n')
        f.write(report)
    print(f'候補リスト保存: {out_path}')

if __name__ == '__main__':
    main()
