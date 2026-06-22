from flask import Flask, request, jsonify
import json, os, anthropic, urllib.request, threading
from get_line_token import get_line_token

app = Flask(__name__)

LINE_CHANNEL_TOKEN = get_line_token()
LINE_USER_ID = 'U206a030c1759f1ed8f4c684d03d11915'
REPORT_CACHE = os.path.expanduser('~/lodgers/agents/hojyokin_last_report.json')
DOCS_OUTPUT = os.path.expanduser('~/lodgers/agents/hojyokin_draft_docs.txt')

client = anthropic.Anthropic()

COMPANY_PROFILE = """
【申請事業者情報】
・会社名：株式会社芹江コンチェルト
・代表者：芹江匡晋（元プロボクシング日本スーパーバンタム級第35代チャンピオン）
・所在地：栃木県那須塩原市黒磯
・事業①：Lodgers Bldg SERIE（旅館業・簡易宿所・民泊）/ 料金6,000円〜/泊 / OTA: Booking.com・Airbnb・VRBO
・事業②：パンダベビーカステラ（キッチンカー・食品販売・マルシェ出店）
・事業③：Honey LaRva（フィットネスボクシングジム / 大田原市・那須塩原市の直営2店舗）
"""

def send_line_message(message):
    data = json.dumps({'to': LINE_USER_ID, 'messages': [{'type': 'text', 'text': message}]}).encode('utf-8')
    req = urllib.request.Request('https://api.line.me/v2/bot/message/push', data=data,
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + LINE_CHANNEL_TOKEN})
    urllib.request.urlopen(req)

def generate_application_drafts(report_text):
    prompt = f'''あなたは中小企業診断士です。以下の事業者情報と補助金レポートをもとに、各補助金の申請書類の下書きを作成してください。

{COMPANY_PROFILE}

【補助金レポート】
{report_text}

━━━━━━━━━━━━━━━━━━━━
各補助金について以下の形式で下書きを作成してください：

📋【補助金名】

■ 事業概要（申請書記載用・200字程度）
→ 実際に記入できる文章を書く

■ 補助事業の必要性・目的（申請書記載用・200字程度）
→ 実際に記入できる文章を書く

■ 期待される効果（申請書記載用・150字程度）
→ 実際に記入できる文章を書く

■ 事業スケジュール（例）
→ 月別の実施計画を箇条書きで

■ 補助対象経費の内訳（例）
→ 費目・金額・内容を表形式で

■ 提出書類チェックリスト
→ □ 必要書類を列挙

━━━━━━━━━━━━━━━━━━━━

事業者の実情（元チャンピオン経営・地域密着・3事業展開・黒磯駅エリア活性化）を活かした
説得力ある文章にしてください。ですます調。'''

    response = client.messages.create(
        model='claude-sonnet-4-6',
        max_tokens=4000,
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response.content[0].text

def split_and_send(message, chunk_size=4000):
    """LINEの文字数制限(5000字)に合わせて分割送信"""
    lines = message.split('\n')
    current = ''
    part = 1
    for line in lines:
        if len(current) + len(line) + 1 > chunk_size:
            send_line_message(f'（{part}）\n' + current.strip())
            current = ''
            part += 1
        current += line + '\n'
    if current.strip():
        send_line_message(f'（{part}）\n' + current.strip())

def handle_apply_yes():
    send_line_message('📂 申請書類の下書きを作成しています...\n各補助金の事業概要・必要性・期待効果・経費内訳まで作ります。\n少々お待ちください⏳')
    if not os.path.exists(REPORT_CACHE):
        send_line_message('⚠️ 補助金レポートのキャッシュがありません。先に補助金エージェントを実行してください。')
        return
    with open(REPORT_CACHE, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    report_text = cache.get('report', '')
    updated = cache.get('updated', '')
    if not report_text:
        send_line_message('⚠️ 直近の補助金レポートが見つかりませんでした。先に補助金エージェントを実行してください。')
        return
    docs = generate_application_drafts(report_text)
    with open(DOCS_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(f'申請書類下書き生成日時: {updated}\n\n')
        f.write(docs)
    send_line_message(f'✅ 申請書類の下書きが完成しました！（{updated}分）\n以下に各補助金の記入文案をお送りします👇')
    split_and_send(docs)
    send_line_message('📌 この下書きをそのまま申請書にコピー＆ペーストしてご利用ください。\n修正・追記が必要な箇所はレイディに声をかけてください！')

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(json.dumps(data, indent=2, ensure_ascii=False))
    for event in data.get('events', []):
        user_id = event.get('source', {}).get('userId', 'なし')
        print(f'\n★★★ User ID: {user_id} ★★★\n')
        if event.get('type') == 'message' and event['message'].get('type') == 'text':
            text = event['message']['text'].strip()
            if text == 'hojyokin_apply:はい':
                threading.Thread(target=handle_apply_yes).start()
            elif text == 'hojyokin_apply:いいえ':
                send_line_message('👍 分かりました！必要な時はいつでも声をかけてください。')
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(port=8080)
