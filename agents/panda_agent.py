import os, json, anthropic
from datetime import datetime

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

【東京23区エリア】以下のキーワードで検索：
1. 東京23区 キッチンカー 出店募集 2026年
2. 東京 ベビーカステラ マルシェ イベント出店 募集 2026
3. 東京23区 物産展 食品 出店者募集 2026
4. 東京 キッチンカー フェス マルシェ 出店申込 2026年6月7月
5. 東京 栃木 物産展 出店 2026 申込

【栃木県エリア】以下のキーワードで検索：
6. 栃木県 キッチンカー マルシェ 出店募集 2026
7. 栃木県 物産展 イベント 出店者募集 2026
8. 宇都宮 那須 日光 キッチンカー フェス 出店申込 2026

各検索結果から以下を必ず記載すること：
- イベント名・開催場所（東京or栃木を明記）
- 開催日時
- 申込URL（実際のURLを記載）
- 申込締切日

絶対禁止：問い合わせてください・確認してください・見つかりませんでした・URLが見つかりません

出力：【パンダカステラ販路レポート】{today}
＜東京23区＞と＜栃木県＞に分けて記載。800文字以内。最後に今週すぐ申し込めるアクション1つ（URLつき）"""
CATEGORY = 'パンダカステラ'

def main():
    today = datetime.now().strftime('%Y/%m/%d')
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