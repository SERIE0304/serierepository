import os, json, anthropic
from datetime import datetime
from activity_logger import log_activity

client = anthropic.Anthropic()
from get_line_token import get_line_token
LINE_CHANNEL_TOKEN = get_line_token()
LINE_USER_ID = 'U206a030c1759f1ed8f4c684d03d11915'
TASKS_FILE = os.path.expanduser('~/lodgers/agents/tasks.json')

def send_line_message(message):
    import urllib.request
    data = json.dumps({'to': LINE_USER_ID, 'messages': [{'type': 'text', 'text': message}]}).encode('utf-8')
    req = urllib.request.Request('https://api.line.me/v2/bot/message/push', data=data,
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + LINE_CHANNEL_TOKEN})
    urllib.request.urlopen(req)

def save_task(cat, task_text):
    data = {'tasks': []}
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r', encoding='utf-8') as f: data = json.load(f)
    data['tasks'].append({'category': cat, 'task': task_text, 'done': False,
        'added': datetime.now().strftime('%Y/%m/%d'), 'week': datetime.now().strftime('%Y-W%W')})
    with open(TASKS_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=2)

PROMPT = """今日は{today}です。以下のキーワードでGoogle検索して具体的な出店募集情報を報告してください。

検索キーワード：
1. 東京 キッチンカー 出店募集 2026年6月
2. 代々木公園 マルシェ 出店者募集 2026
3. 吉祥寺 二子玉川 マルシェ キッチンカー 募集 2026
4. 東京 物産展 栃木 出店 2026年6月 申込
5. とちぎ物産展 銀座matsuri 2026 出店申込

各検索結果から：
- イベント名
- 開催日時・場所
- 申込URL
- 締切日
を具体的に記載すること。

絶対禁止：問い合わせてください・確認してください・見つかりませんでした

出力：【パンダカステラ販路レポート】{today}
600文字以内・最後に今週すぐ申し込めるアクション1つ"""
CATEGORY = 'パンダカステラ'

def main():
    today = datetime.now().strftime('%Y/%m/%d')
    log_activity('システム自動実行', 'agent', 'パンダカステラエージェント')
    print('パンダカステラエージェント実行中...')
    p = PROMPT.replace('{today}', today)
    report_raw = client.messages.create(tools=[{"type":"web_search_20250305","name":"web_search"}], model='claude-sonnet-4-5', max_tokens=1500,
        messages=[{'role': 'user', 'content': p}])
    full_text = ''
    for block in report_raw.content:
        if hasattr(block, 'text'):
            full_text += block.text
    report = full_text
    print(report)
    send_line_message(report)
    print('LINE送信完了！')
    task = client.messages.create(model='claude-haiku-4-5-20251001', max_tokens=100,
        messages=[{'role': 'user', 'content': '以下から今週やるべきアクションを1行で抽出:' + report}])
    full_text = ''
    for block in report_raw.content:
        if hasattr(block, 'text'):
            full_text += block.text
    report = full_text.strip()
    pass  # save_task一時無効
    print('タスク保存：' + str(task))

if __name__ == '__main__': main()