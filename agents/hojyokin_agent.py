import os, json, anthropic
from datetime import datetime
from activity_logger import log_activity, save_report

from get_api_key import get_api_key
client = anthropic.Anthropic(api_key=get_api_key())
from get_line_token import get_line_token
LINE_CHANNEL_TOKEN = get_line_token()
LINE_USER_ID = 'Ud31d803ed53ed4c8f7af94acf4e5a5d4'
TASKS_FILE = os.path.join(os.path.dirname(__file__), 'tasks.json')

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

PROMPT = '今日は{today}です。株式会社芹江コンチェルト（栃木県那須塩原市黒磯）の3事業の補助金を調査。旅館業SERIE・パンダベビーカステラ・Honey LaRva。那須塩原市・栃木県・国の補助金を緊急30日以内・今月中・次回公募待ちで整理。冒頭【補助金レポート】{today} 絵文字使用・各3行以内・600文字以内・ですます調・最後に今週のアクション1つ'
CATEGORY = '補助金'

def main():
    today = datetime.now().strftime('%Y/%m/%d')
    log_activity('システム自動実行', 'agent', CATEGORY + 'エージェント')
    print(CATEGORY + ' エージェント実行中...')
    p = PROMPT.replace('{today}', today)
    report_raw = client.messages.create(tools=[{"type":"web_search_20250305","name":"web_search"}], model='claude-sonnet-4-5', max_tokens=1500,
        messages=[{'role': 'user', 'content': p}])
    full_text = ''
    for block in report_raw.content:
        if hasattr(block, 'text'):
            full_text += block.text
    report = full_text
    print(report)
    save_report('hojyokin', report)
    send_line_message(report)
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