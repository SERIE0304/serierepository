import os, json, re, anthropic
from flask import Flask, request, jsonify
from get_line_token import get_line_token

app = Flask(__name__)
client = anthropic.Anthropic()

# 社長（芹江）として認識するキーワード
PRESIDENT_NAMES = ['芹江', '社長', 'serie', 'masaaki']

# 登録済み社員名リスト（必要に応じて追加）
EMPLOYEE_NAMES = ['スタッフ', '社員', 'staff']

SYSTEM_PRESIDENT = """あなたはLeidy（レイディ）です。株式会社芹江コンチェルトの社長・芹江匡晋さん専属のAIアシスタントです。
芹江さんは元プロボクシング日本スーパーバンタム級35代チャンピオンで、現在は以下の事業を経営しています：
- Lodgers Bldg SERIE（栃木県那須塩原市の旅館業）
- Honey LaRva（フィットネスボクシングジム・大田原市・那須塩原市2店舗）
- パンダベビーカステラ（移動販売）

【社長モードの対応方針】
- 経営者・意思決定者として対応
- 戦略・数字・ROIを重視した提案
- 直接的・簡潔に要点を伝える
- 「社長」または「芹江さん」と呼びかける
- 忙しい経営者の時間を尊重し、結論から述べる
- 補助金・FC化・不動産・SNS戦略など経営全般に精通している
"""

SYSTEM_EMPLOYEE = """あなたはLeidy（レイディ）です。株式会社芹江コンチェルトのスタッフ向けAIアシスタントです。
この会社は以下の事業を運営しています：
- Lodgers Bldg SERIE（栃木県那須塩原市の旅館業）
- Honey LaRva（フィットネスボクシングジム）
- パンダベビーカステラ（移動販売）

【社員モードの対応方針】
- スタッフの業務をサポートする視点で対応
- 手順・マニュアル・チェックリスト形式で伝える
- わかりやすく・丁寧に・ステップを明確に
- 「〜さん」と呼びかける
- 現場で即実行できる具体的なアドバイスを優先
- 社長への報告・相談事項がある場合は明示する
"""

SYSTEM_DEFAULT = """あなたはLeidy（レイディ）です。株式会社芹江コンチェルトのAIアシスタントです。
親切・丁寧・的確に対応します。メッセージの冒頭に名前を書くと、その人のロールに合った対応に切り替わります。
例：「芹江 今月の売上は...」→ 社長モード
例：「スタッフ チェックイン手順を教えて」→ 社員モード
"""

def detect_role(text: str) -> tuple[str, str, str]:
    """メッセージ冒頭の名前からロールを判定。(role, name, message_body)を返す"""
    first_word = text.split()[0] if text.split() else ''
    first_line = text.split('\n')[0]

    for name in PRESIDENT_NAMES:
        if first_word.lower().startswith(name.lower()) or first_line.lower().startswith(name.lower()):
            body = re.sub(r'^' + re.escape(first_word), '', text, count=1).strip()
            return 'president', first_word, body or text

    for name in EMPLOYEE_NAMES:
        if first_word.lower().startswith(name.lower()) or first_line.lower().startswith(name.lower()):
            body = re.sub(r'^' + re.escape(first_word), '', text, count=1).strip()
            return 'employee', first_word, body or text

    # 社員名が登録されている場合の動的チェック（将来の拡張用）
    return 'default', '', text

def get_system_prompt(role: str) -> str:
    if role == 'president':
        return SYSTEM_PRESIDENT
    elif role == 'employee':
        return SYSTEM_EMPLOYEE
    return SYSTEM_DEFAULT

def ask_leidy(role: str, user_name: str, message: str) -> str:
    system = get_system_prompt(role)
    response = client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=800,
        system=system,
        messages=[{'role': 'user', 'content': message}]
    )
    return response.content[0].text

def reply_line(reply_token: str, message: str):
    token = get_line_token()
    data = json.dumps({
        'replyToken': reply_token,
        'messages': [{'type': 'text', 'text': message}]
    }).encode('utf-8')
    import urllib.request
    req = urllib.request.Request(
        'https://api.line.me/v2/bot/message/reply',
        data=data,
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
    )
    urllib.request.urlopen(req)

@app.route('/leidy', methods=['POST'])
def leidy_webhook():
    data = request.json
    for event in data.get('events', []):
        if event.get('type') != 'message':
            continue
        msg = event.get('message', {})
        if msg.get('type') != 'text':
            continue

        text = msg.get('text', '').strip()
        reply_token = event.get('replyToken')

        role, detected_name, body = detect_role(text)

        role_label = {'president': '👑 社長モード', 'employee': '👤 社員モード', 'default': '❓ 確認中'}[role]
        print(f"[Leidy] ロール: {role_label} | 名前: {detected_name or '検出なし'} | 本文: {body[:30]}...")

        if role == 'default':
            reply_line(reply_token, 'こんにちは、Leidyです。\nどなたが使用していますか？\n\n例：「芹江 〇〇について教えて」のようにメッセージの冒頭にお名前を入れていただくと、より適切にサポートできます。')
            return jsonify({'status': 'ok'})

        reply = ask_leidy(role, detected_name, body)
        prefix = f"[{role_label}]\n"
        reply_line(reply_token, prefix + reply)

    return jsonify({'status': 'ok'})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'Leidy is alive'})

if __name__ == '__main__':
    print('Leidy エージェント起動中... ポート8081')
    app.run(port=8081, debug=False)
