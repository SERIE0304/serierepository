from flask import Flask, request, jsonify
import json, os, anthropic, urllib.request, threading
from get_line_token import get_line_token

app = Flask(__name__)

LINE_CHANNEL_TOKEN = get_line_token()
LINE_USER_ID = 'U206a030c1759f1ed8f4c684d03d11915'
REPORT_CACHE = os.path.expanduser('~/lodgers/agents/hojyokin_last_report.json')

client = anthropic.Anthropic()

def send_line_message(message):
    data = json.dumps({'to': LINE_USER_ID, 'messages': [{'type': 'text', 'text': message}]}).encode('utf-8')
    req = urllib.request.Request('https://api.line.me/v2/bot/message/push', data=data,
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + LINE_CHANNEL_TOKEN})
    urllib.request.urlopen(req)

def generate_application_docs(report_text):
    prompt = f'''以下の補助金レポートを元に、各補助金の申請準備資料を作成してください。

{report_text}

【出力形式】各補助金ごとに以下を記載：

━━━━━━━━━━━━━━━━
📋 【補助金名】
■ 申請に必要な書類リスト
■ 準備のポイント（2〜3行）
■ 注意事項
━━━━━━━━━━━━━━━━

株式会社芹江コンチェルト（那須塩原市黒磯）の状況に合わせた具体的なアドバイスを含めてください。
ですます調・絵文字使用。'''
    response = client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=3000,
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response.content[0].text

def handle_apply_yes():
    send_line_message('📂 申請資料を作成しています...\nしばらくお待ちください。')
    report_text = ''
    if os.path.exists(REPORT_CACHE):
        with open(REPORT_CACHE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
            report_text = cache.get('report', '')
            updated = cache.get('updated', '')
        if report_text:
            docs = generate_application_docs(report_text)
            send_line_message(f'📄【申請準備資料】{updated}\n\n' + docs)
        else:
            send_line_message('⚠️ 直近の補助金レポートが見つかりませんでした。先に補助金エージェントを実行してください。')
    else:
        send_line_message('⚠️ 補助金レポートのキャッシュがありません。先に補助金エージェントを実行してください。')

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
