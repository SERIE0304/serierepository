import os, json, anthropic, urllib.request
from datetime import datetime

client = anthropic.Anthropic()
from get_line_token import get_line_token
LINE_CHANNEL_TOKEN = get_line_token()
LINE_USER_ID = 'U206a030c1759f1ed8f4c684d03d11915'
TASKS_FILE = os.path.expanduser('~/lodgers/agents/tasks.json')
REPORT_CACHE = os.path.expanduser('~/lodgers/agents/hojyokin_last_report.json')

def send_line_message(message):
    data = json.dumps({'to': LINE_USER_ID, 'messages': [{'type': 'text', 'text': message}]}).encode('utf-8')
    req = urllib.request.Request('https://api.line.me/v2/bot/message/push', data=data,
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + LINE_CHANNEL_TOKEN})
    urllib.request.urlopen(req)

def send_line_confirm():
    payload = {
        'to': LINE_USER_ID,
        'messages': [{
            'type': 'template',
            'altText': '補助金申請資料の作成依頼',
            'template': {
                'type': 'confirm',
                'text': '📄 ピックアップした補助金の申請資料をレイディに作成してもらいますか？',
                'actions': [
                    {'type': 'message', 'label': 'はい', 'text': 'hojyokin_apply:はい'},
                    {'type': 'message', 'label': 'いいえ', 'text': 'hojyokin_apply:いいえ'}
                ]
            }
        }]
    }
    data = json.dumps(payload).encode('utf-8')
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

def save_report_cache(report_text):
    with open(REPORT_CACHE, 'w', encoding='utf-8') as f:
        json.dump({'report': report_text, 'updated': datetime.now().strftime('%Y/%m/%d %H:%M')}, f, ensure_ascii=False, indent=2)

PROMPT = '''今日は{today}です。以下の対象事業・対象施設向けの補助金を調査してください。

【対象①】株式会社芹江コンチェルト（栃木県那須塩原市黒磯）の3事業
- 旅館業 Lodgers Bldg SERIE（民泊・簡易宿所）
- パンダベビーカステラ（キッチンカー・食品販売）
- Honey LaRva（フィットネスボクシングジム）

【対象②】旅館・簡易宿所・民泊事業者向け補助金（国・栃木県・那須塩原市）
- バリアフリー改修・省エネ設備・防災設備・Wi-Fi整備
- 観光DX・インバウンド対応
- 宿泊施設改修・創業支援

【調査範囲】那須塩原市・栃木県・国（観光庁・経産省・中小企業庁）

【出力形式】
冒頭に「【補助金レポート】{today}」を記載。

以下の形式で補助金をリストアップ（最大10件）:

━━━━━━━━━━━━━━━━
【名称】〇〇補助金
【期日】YYYY/MM/DD（または「公募準備中」「随時」等）
【内容】1〜2行で概要
【URL】https://...（申込・要項ページの正確なURL）
━━━━━━━━━━━━━━━━

全件リストアップ後、最後に「■今週のアクション：〇〇」を1行で記載。
絵文字使用・ですます調。URLは必ず実在するものを記載。'''

CATEGORY = '補助金'

def run_search(prompt_text):
    messages = [{'role': 'user', 'content': prompt_text}]
    report = ''
    for _ in range(15):
        response = client.messages.create(
            model='claude-sonnet-4-6',
            max_tokens=3000,
            tools=[{'type': 'web_search_20250305', 'name': 'web_search'}],
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
    return report

def main():
    today = datetime.now().strftime('%Y/%m/%d')
    print(CATEGORY + ' エージェント実行中...')
    p = PROMPT.replace('{today}', today)
    report = run_search(p)
    print(report)
    save_report_cache(report)
    send_line_message(report)
    print('LINE送信完了！')
    send_line_confirm()
    print('確認メッセージ送信完了！')
    task = client.messages.create(model='claude-haiku-4-5-20251001', max_tokens=100,
        messages=[{'role': 'user', 'content': '以下から今週やるべきアクションを1行で抽出:' + report}]).content[0].text.strip()
    save_task(CATEGORY, task)
    print('タスク保存：' + task)

if __name__ == '__main__': main()
