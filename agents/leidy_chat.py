import anthropic, re, os
from flask import Flask, request, jsonify, render_template_string, session
from activity_logger import log_chat
from get_api_key import get_api_key

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')

AGENT_LABELS = {
    'panda':    'パンダカステラ 販路レポート',
    'hojyokin': '補助金レポート',
    'fudosan':  '不動産レポート',
    'larva':    'Honey LaRva 集客レポート',
    'pricing':  'SERIE 料金提案レポート',
    'fc':       'Honey LaRva FC化調査レポート',
}

app = Flask(__name__)
app.secret_key = 'leidy-serie-concerto'
client = anthropic.Anthropic(api_key=get_api_key())

PRESIDENT_NAMES = ['芹江', '社長', 'serie', 'masaaki']
EMPLOYEE_NAMES = ['スタッフ', '社員', 'staff', '小筆']

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
"""

HTML = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Leidy - 芹江コンチェルト</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Hiragino Sans', 'Meiryo', sans-serif; background: #f0f2f5; height: 100vh; display: flex; flex-direction: column; }
  header { background: #1a1a2e; color: white; padding: 14px 20px; display: flex; align-items: center; gap: 12px; }
  header h1 { font-size: 19px; font-weight: bold; }
  header a { color: #aaa; font-size: 13px; text-decoration: none; border: 1px solid #555; padding: 4px 10px; border-radius: 12px; }
  header .nav { margin-left: auto; display: flex; gap: 8px; }
  header a:hover { color: white; border-color: #aaa; }
  #role-badge { padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; background: #444; color: #ccc; }
  #role-badge.president { background: #c9a84c; color: #1a1a2e; }
  #role-badge.employee { background: #4a9eff; color: white; }
  #chat { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 12px; }
  .msg { max-width: 75%; padding: 12px 16px; border-radius: 18px; line-height: 1.6; font-size: 15px; white-space: pre-wrap; }
  .msg.user { align-self: flex-end; background: #1a1a2e; color: white; border-bottom-right-radius: 4px; }
  .msg.leidy { align-self: flex-start; background: white; color: #333; border-bottom-left-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
  .msg.system { align-self: center; background: #e8e8e8; color: #666; font-size: 13px; padding: 8px 16px; border-radius: 20px; }
  #input-area { padding: 14px 18px; background: white; border-top: 1px solid #e0e0e0; display: flex; gap: 10px; }
  #msg-input { flex: 1; padding: 12px 16px; border: 2px solid #e0e0e0; border-radius: 24px; font-size: 15px; font-family: inherit; outline: none; resize: none; max-height: 120px; }
  #msg-input:focus { border-color: #1a1a2e; }
  #send-btn { padding: 12px 22px; background: #1a1a2e; color: white; border: none; border-radius: 24px; font-size: 15px; cursor: pointer; }
  #send-btn:disabled { background: #ccc; cursor: not-allowed; }
  .hint { font-size: 12px; color: #999; text-align: center; padding: 5px; }

  /* 履歴ページ */
  .history-wrap { max-width: 800px; margin: 30px auto; padding: 0 20px; }
  .history-wrap h2 { margin-bottom: 20px; color: #1a1a2e; }
  .log-item { background: white; border-radius: 12px; padding: 14px 18px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
  .log-item .meta { font-size: 12px; color: #999; margin-bottom: 6px; }
  .log-item .user-tag { display: inline-block; padding: 2px 10px; border-radius: 10px; font-size: 12px; font-weight: bold; margin-right: 8px; }
  .tag-president { background: #c9a84c; color: #1a1a2e; }
  .tag-employee { background: #4a9eff; color: white; }
  .tag-agent { background: #6c757d; color: white; }
  .log-item .q { color: #333; margin-bottom: 4px; }
  .log-item .a { color: #666; font-size: 14px; border-left: 3px solid #e0e0e0; padding-left: 10px; margin-top: 6px; }
  .filter-bar { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
  .filter-btn { padding: 6px 16px; border: 2px solid #ddd; border-radius: 20px; background: white; cursor: pointer; font-size: 13px; }
  .filter-btn.active { border-color: #1a1a2e; background: #1a1a2e; color: white; }
</style>
</head>
<body>
<header>
  <div>
    <h1>Leidy</h1>
  </div>
  <div id="role-badge">未設定</div>
  <div class="nav">
    <a href="/reports">📄 資料</a>
    <a href="/history">📋 履歴</a>
  </div>
</header>
<div id="chat">
  <div class="msg system">「芹江です」または「スタッフです」と話しかけてください</div>
  <div class="msg leidy">こんにちは、Leidyです。どなたが使用していますか？\n\n「芹江です」→ 社長モードに切り替わります\n「スタッフです」→ 社員モードに切り替わります</div>
</div>
<p class="hint">一度名乗るとセッション中はモードが維持されます</p>
<div id="input-area">
  <textarea id="msg-input" placeholder="例：芹江です　または　補助金の状況は？" rows="1"></textarea>
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

function updateBadge(role, userName) {
  badge.className = '';
  if (role === 'president') { badge.className = 'president'; badge.textContent = '👑 ' + (userName || '社長') + ' モード'; }
  else if (role === 'employee') { badge.className = 'employee'; badge.textContent = '👤 ' + (userName || 'スタッフ') + ' モード'; }
  else { badge.textContent = '未設定'; }
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
    const res = await fetch('/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: text})
    });
    const data = await res.json();
    thinking.remove();
    addMsg(data.reply, 'leidy');
    updateBadge(data.role, data.user_name);
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

HISTORY_HTML = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>Leidy 活動履歴</title>
<style>
  body { font-family: 'Hiragino Sans','Meiryo',sans-serif; background:#f0f2f5; }
  .history-wrap { max-width:800px; margin:30px auto; padding:0 20px; }
  h2 { margin-bottom:20px; color:#1a1a2e; }
  a.back { display:inline-block; margin-bottom:20px; color:#1a1a2e; text-decoration:none; font-size:14px; }
  .filter-bar { display:flex; gap:10px; margin-bottom:20px; flex-wrap:wrap; }
  .filter-btn { padding:6px 16px; border:2px solid #ddd; border-radius:20px; background:white; cursor:pointer; font-size:13px; }
  .log-item { background:white; border-radius:12px; padding:14px 18px; margin-bottom:12px; box-shadow:0 1px 3px rgba(0,0,0,0.08); }
  .meta { font-size:12px; color:#999; margin-bottom:6px; }
  .user-tag { display:inline-block; padding:2px 10px; border-radius:10px; font-size:12px; font-weight:bold; margin-right:8px; }
  .tag-president { background:#c9a84c; color:#1a1a2e; }
  .tag-employee { background:#4a9eff; color:white; }
  .tag-agent { background:#6c757d; color:white; }
  .q { color:#333; margin-bottom:4px; }
  .a { color:#666; font-size:14px; border-left:3px solid #e0e0e0; padding-left:10px; margin-top:6px; white-space:pre-wrap; }
  .empty { color:#999; text-align:center; padding:40px; }
</style>
</head>
<body>
<div class="history-wrap">
  <a class="back" href="/">← チャットに戻る</a>
  <h2>活動履歴</h2>
  {% if not activities %}
  <p class="empty">まだ履歴がありません</p>
  {% else %}
  {% for a in activities %}
  <div class="log-item">
    <div class="meta">
      {% if a.role == 'president' or a.user == '芹江' %}
      <span class="user-tag tag-president">👑 {{ a.user }}</span>
      {% elif a.action == 'agent' %}
      <span class="user-tag tag-agent">🤖 自動実行</span>
      {% else %}
      <span class="user-tag tag-employee">👤 {{ a.user }}</span>
      {% endif %}
      {{ a.timestamp }}
      {% if a.action != 'leidy_chat' %} ／ {{ a.action }}{% endif %}
    </div>
    {% if a.action == 'leidy_chat' %}
    <div class="q">Q: {{ a.question }}</div>
    <div class="a">{{ a.answer[:300] }}{% if a.answer|length > 300 %}...{% endif %}</div>
    {% else %}
    <div class="q">{{ a.detail }}</div>
    {% endif %}
  </div>
  {% endfor %}
  {% endif %}
</div>
</body>
</html>
"""

def detect_role(text, current_role, current_user):
    """名乗り検出（セッション継続も考慮）"""
    t = text.strip()
    # 名乗りパターン：「芹江です」「スタッフです」など
    for name in PRESIDENT_NAMES:
        if re.match(rf'^{name}', t, re.IGNORECASE):
            body = re.sub(rf'^{name}(です|だ|。|　|\s)*', '', t, flags=re.IGNORECASE).strip()
            return 'president', name, body or t
    for name in EMPLOYEE_NAMES:
        if re.match(rf'^{name}', t, re.IGNORECASE):
            body = re.sub(rf'^{name}(です|だ|。|　|\s)*', '', t, flags=re.IGNORECASE).strip()
            return 'employee', name, body or t
    # セッションで既に名乗っていればそのモード継続
    if current_role in ('president', 'employee'):
        return current_role, current_user, t
    return 'default', '', t

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    text = data.get('message', '').strip()

    current_role = session.get('role', 'default')
    current_user = session.get('user_name', '')

    role, user_name, body = detect_role(text, current_role, current_user)

    if role == 'default':
        return jsonify({'role': 'default', 'user_name': '', 'reply': 'どなたが使用していますか？\n\n「芹江です」または「スタッフです」と最初に教えていただくと、その方に合った対応ができます。'})

    # セッションに記憶
    session['role'] = role
    session['user_name'] = user_name

    # 名乗りだけで本文がない場合
    if not body or body == text:
        label = '社長' if role == 'president' else 'スタッフ'
        reply = f'了解しました、{user_name}さん（{label}モード）。何でもお聞きください！'
        log_chat(user_name, role, text, reply)
        return jsonify({'role': role, 'user_name': user_name, 'reply': reply})

    system = SYSTEM_PRESIDENT if role == 'president' else SYSTEM_EMPLOYEE
    response = client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=800,
        system=system,
        messages=[{'role': 'user', 'content': body}]
    )
    reply = response.content[0].text
    log_chat(user_name, role, body, reply)
    return jsonify({'role': role, 'user_name': user_name, 'reply': reply})

REPORTS_HTML = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>資料一覧 - Leidy</title>
<style>
  body { font-family: 'Hiragino Sans','Meiryo',sans-serif; background:#f0f2f5; }
  .wrap { max-width:700px; margin:30px auto; padding:0 20px; }
  a.back { display:inline-block; margin-bottom:20px; color:#1a1a2e; text-decoration:none; font-size:14px; }
  h2 { margin-bottom:20px; color:#1a1a2e; }
  .card { background:white; border-radius:12px; padding:20px 24px; margin-bottom:16px; box-shadow:0 1px 3px rgba(0,0,0,0.08); display:flex; align-items:center; justify-content:space-between; }
  .card-info h3 { font-size:16px; color:#1a1a2e; margin-bottom:4px; }
  .card-info .meta { font-size:12px; color:#999; }
  .btn { padding:10px 20px; background:#1a1a2e; color:white; border:none; border-radius:20px; font-size:14px; cursor:pointer; text-decoration:none; }
  .btn:hover { background:#2d2d4e; }
  .empty { color:#999; text-align:center; padding:40px; }
</style>
</head>
<body>
<div class="wrap">
  <a class="back" href="/">← チャットに戻る</a>
  <h2>📄 資料一覧</h2>
  <p style="font-size:13px;color:#666;margin-bottom:20px;">社長が作ったエージェントのレポートです。クリックして印刷できます。</p>
  {% if not reports %}
  <p class="empty">まだ資料がありません。<br>エージェントを実行するとここに表示されます。</p>
  {% else %}
  {% for r in reports %}
  <div class="card">
    <div class="card-info">
      <h3>{{ r.label }}</h3>
      <div class="meta">最終更新: {{ r.updated }}</div>
    </div>
    <a class="btn" href="/report/{{ r.name }}">開く・印刷</a>
  </div>
  {% endfor %}
  {% endif %}
</div>
</body>
</html>
"""

REPORT_DETAIL_HTML = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{{ label }} - 印刷</title>
<style>
  body { font-family: 'Hiragino Sans','Meiryo',sans-serif; max-width:700px; margin:30px auto; padding:0 20px; }
  .noprint { margin-bottom:20px; display:flex; gap:10px; }
  .noprint a { color:#1a1a2e; text-decoration:none; font-size:14px; border:1px solid #ccc; padding:6px 14px; border-radius:20px; }
  .print-btn { padding:8px 20px; background:#1a1a2e; color:white; border:none; border-radius:20px; font-size:14px; cursor:pointer; }
  h1 { font-size:20px; color:#1a1a2e; margin-bottom:4px; }
  .meta { font-size:12px; color:#999; margin-bottom:20px; }
  .content { white-space:pre-wrap; line-height:1.8; font-size:15px; color:#333; border-top:2px solid #1a1a2e; padding-top:16px; }
  @media print { .noprint { display:none; } body { margin:0; } }
</style>
</head>
<body>
<div class="noprint">
  <a href="/reports">← 資料一覧</a>
  <button class="print-btn" onclick="window.print()">🖨️ 印刷する</button>
</div>
<h1>{{ label }}</h1>
<div class="meta">{{ updated }}</div>
<div class="content">{{ content }}</div>
</body>
</html>
"""

@app.route('/reports')
def reports():
    items = []
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for name, label in AGENT_LABELS.items():
        path = os.path.join(OUTPUT_DIR, f'{name}_latest.txt')
        if os.path.exists(path):
            mtime = os.path.getmtime(path)
            from datetime import datetime as dt
            updated = dt.fromtimestamp(mtime).strftime('%Y/%m/%d %H:%M')
            items.append({'name': name, 'label': label, 'updated': updated})
    return render_template_string(REPORTS_HTML, reports=items)

@app.route('/report/<name>')
def report_detail(name):
    if name not in AGENT_LABELS:
        return '資料が見つかりません', 404
    path = os.path.join(OUTPUT_DIR, f'{name}_latest.txt')
    if not os.path.exists(path):
        return '資料がまだありません。エージェントを実行してください。', 404
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    updated = lines[0].replace('生成日時: ', '').strip() if lines else ''
    content = ''.join(lines[2:]) if len(lines) > 2 else ''
    return render_template_string(REPORT_DETAIL_HTML,
        label=AGENT_LABELS[name], updated=updated, content=content)

@app.route('/history')
def history():
    from activity_logger import load_log
    data = load_log()
    acts = list(reversed(data.get('activities', [])))
    return render_template_string(HISTORY_HTML, activities=acts)

if __name__ == '__main__':
    print('Leidy 起動中... http://localhost:5000 をブラウザで開いてください')
    app.run(port=5000, debug=False)
