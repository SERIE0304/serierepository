import anthropic
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
client = anthropic.Anthropic()

PRESIDENT_NAMES = ['芹江', '社長', 'serie', 'masaaki']
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
- 現場で即実行できる具体的なアドバイスを優先
- 社長への報告・相談事項がある場合は明示する
"""

HTML = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Leidy - 芹江コンチェルト AIアシスタント</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Hiragino Sans', 'Meiryo', sans-serif; background: #f0f2f5; height: 100vh; display: flex; flex-direction: column; }
  header { background: #1a1a2e; color: white; padding: 16px 24px; display: flex; align-items: center; gap: 12px; }
  header h1 { font-size: 20px; font-weight: bold; }
  header span { font-size: 13px; color: #aaa; }
  #role-badge { padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; background: #444; color: #ccc; margin-left: auto; }
  #role-badge.president { background: #c9a84c; color: #1a1a2e; }
  #role-badge.employee { background: #4a9eff; color: white; }
  #chat { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 12px; }
  .msg { max-width: 75%; padding: 12px 16px; border-radius: 18px; line-height: 1.6; font-size: 15px; white-space: pre-wrap; }
  .msg.user { align-self: flex-end; background: #1a1a2e; color: white; border-bottom-right-radius: 4px; }
  .msg.leidy { align-self: flex-start; background: white; color: #333; border-bottom-left-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
  .msg.system { align-self: center; background: #e8e8e8; color: #666; font-size: 13px; padding: 8px 16px; border-radius: 20px; }
  #input-area { padding: 16px 20px; background: white; border-top: 1px solid #e0e0e0; display: flex; gap: 10px; }
  #msg-input { flex: 1; padding: 12px 16px; border: 2px solid #e0e0e0; border-radius: 24px; font-size: 15px; font-family: inherit; outline: none; resize: none; max-height: 120px; }
  #msg-input:focus { border-color: #1a1a2e; }
  #send-btn { padding: 12px 24px; background: #1a1a2e; color: white; border: none; border-radius: 24px; font-size: 15px; cursor: pointer; font-family: inherit; }
  #send-btn:hover { background: #2d2d4e; }
  #send-btn:disabled { background: #ccc; cursor: not-allowed; }
  .hint { font-size: 12px; color: #999; text-align: center; padding: 6px; }
</style>
</head>
<body>
<header>
  <div>
    <h1>Leidy</h1>
    <span>芹江コンチェルト AIアシスタント</span>
  </div>
  <div id="role-badge">モード未設定</div>
</header>
<div id="chat">
  <div class="msg system">冒頭にお名前を入力するとモードが切り替わります</div>
  <div class="msg leidy">こんにちは、Leidyです。どなたが使用していますか？\n\nメッセージの冒頭にお名前を入れてください。\n例：「芹江 今日の予約状況は？」\n例：「スタッフ チェックイン手順を教えて」</div>
</div>
<p class="hint">冒頭に「芹江」→ 社長モード ／ 「スタッフ」→ 社員モード</p>
<div id="input-area">
  <textarea id="msg-input" placeholder="メッセージを入力（例：芹江 補助金の状況は？）" rows="1"></textarea>
  <button id="send-btn" onclick="sendMessage()">送信</button>
</div>
<script>
const input = document.getElementById('msg-input');
const chat = document.getElementById('chat');
const badge = document.getElementById('role-badge');

input.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});
input.addEventListener('input', () => {
  input.style.height = 'auto';
  input.style.height = input.scrollHeight + 'px';
});

function addMsg(text, cls) {
  const div = document.createElement('div');
  div.className = 'msg ' + cls;
  div.textContent = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
  return div;
}

function updateBadge(role) {
  badge.className = '';
  if (role === 'president') { badge.className = 'president'; badge.textContent = '👑 社長モード'; }
  else if (role === 'employee') { badge.className = 'employee'; badge.textContent = '👤 社員モード'; }
  else { badge.className = ''; badge.textContent = 'モード未設定'; }
}

async function sendMessage() {
  const text = input.value.trim();
  if (!text) return;
  const btn = document.getElementById('send-btn');
  btn.disabled = true;
  addMsg(text, 'user');
  input.value = '';
  input.style.height = 'auto';
  const thinking = addMsg('入力中...', 'leidy');
  thinking.style.color = '#999';
  try {
    const res = await fetch('/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({message: text}) });
    const data = await res.json();
    thinking.remove();
    addMsg(data.reply, 'leidy');
    updateBadge(data.role);
  } catch(e) {
    thinking.textContent = 'エラーが発生しました。';
  }
  btn.disabled = false;
  input.focus();
}
</script>
</body>
</html>
"""

def detect_role(text):
    first_word = text.split()[0] if text.split() else ''
    import re
    for name in PRESIDENT_NAMES:
        if first_word.lower().startswith(name.lower()):
            body = re.sub(r'^\S+\s*', '', text, count=1).strip()
            return 'president', first_word, body or text
    for name in EMPLOYEE_NAMES:
        if first_word.lower().startswith(name.lower()):
            body = re.sub(r'^\S+\s*', '', text, count=1).strip()
            return 'employee', first_word, body or text
    return 'default', '', text

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    text = data.get('message', '').strip()
    role, detected_name, body = detect_role(text)

    if role == 'default':
        return jsonify({'role': 'default', 'reply': 'どなたが使用していますか？\n\nメッセージの冒頭にお名前を入れていただくと、その方に合った対応ができます。\n例：「芹江 〇〇について教えて」\n例：「スタッフ 〇〇の手順は？」'})

    system = SYSTEM_PRESIDENT if role == 'president' else SYSTEM_EMPLOYEE
    response = client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=800,
        system=system,
        messages=[{'role': 'user', 'content': body}]
    )
    return jsonify({'role': role, 'reply': response.content[0].text})

if __name__ == '__main__':
    print('Leidy 起動中... http://localhost:5000 をブラウザで開いてください')
    app.run(port=5000, debug=False)
