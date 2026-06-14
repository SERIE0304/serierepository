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

def main():
    today = datetime.now().strftime('%Y/%m/%d')
    print('SERIE料金・稼働率エージェント実行中...')

    prompt = f"""Web検索で「那須塩原 黒磯 ホテル 民泊 料金」を検索し、那須塩原市中央町3-12から近い順に施設名・1泊料金・★評価・距離kmを3件リストアップしてください。次に「那須塩原 イベント 2026年6月」を検索してイベントを1つ見つけてください。それだけで以下の形式でレポートを作成してください。300文字以内厳守。

【SERIE料金レポート】{today}
■競合（黒磯駅周辺）
・施設名 ¥料金 ★評価 距離km
・施設名 ¥料金 ★評価 距離km
・施設名 ¥料金 ★評価 距離km
■推奨料金
今週：平日¥X 土日¥X
来週：平日¥X 土日¥X
■理由：（イベント名と需要を1行で）
■アクション：（1行で）"""

    messages = [{'role': 'user', 'content': prompt}]
    report = ""

    for _ in range(10):
        response = client.messages.create(
            model='claude-sonnet-4-6',
            max_tokens=1000,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=messages
        )
        messages.append({'role': 'assistant', 'content': response.content})

        tool_results = []
        for block in response.content:
            if hasattr(block, 'text') and block.text:
                report = block.text
            if block.type == 'tool_use':
                tool_results.append({'type': 'tool_result', 'tool_use_id': block.id, 'content': '検索完了'})

        if response.stop_reason == 'end_turn':
            break
        if tool_results:
            messages.append({'role': 'user', 'content': tool_results})

    print(report)
    send_line_message(report)
    print('LINE送信完了！')

    task = client.messages.create(model='claude-haiku-4-5-20251001', max_tokens=100,
        messages=[{'role': 'user', 'content': '以下から今週やるべきアクションを1行で抽出：' + report}]).content[0].text.strip()
    save_task('SERIE料金', task)
    print('タスク保存：' + task)

if __name__ == '__main__': main()
