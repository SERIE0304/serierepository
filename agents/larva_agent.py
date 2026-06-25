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

PROMPT = '今日は{today}です。フィットネスボクシングジムHoney LaRva（栃木県大田原市・那須塩原市）の会員獲得と自治体連携情報を調査してください。【1】自治体連携：那須塩原市・大田原市・那須町の健康増進事業・健康ポイント事業・特定保健指導との連携可能性と担当窓口。【2】法人契約：ベネフィットワン・リロクラブ等福利厚生サービスへの登録方法と地域企業への営業方法。【3】地域イベント：那須塩原市・大田原市・那須町の健康・スポーツイベントへの協賛・出展チャンス。【4】集客トレンド：フィットネス業界の最新集客方法（SNS・体験会・紹介制度）。出力：冒頭【Honey LaRvaレポート】{today} 絵文字使用・各3行以内・600文字以内・ですます調・最後に今週のアクション1つ'
CATEGORY = 'HoneyLaRva'

def main():
    today = datetime.now().strftime('%Y/%m/%d')
    log_activity('システム自動実行', 'agent', 'Honey LaRvaエージェント')
    print('Honey LaRvaエージェント実行中...')
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