import os, json, anthropic
from datetime import datetime
from activity_logger import log_activity, save_report

from get_api_key import get_api_key
client = anthropic.Anthropic(api_key=get_api_key())
from get_line_token import get_line_token
LINE_CHANNEL_TOKEN = get_line_token()
LINE_USER_ID = 'U206a030c1759f1ed8f4c684d03d11915'
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

PROMPT = "今日は{today}です。栃木県那須塩原市の不動産売買物件情報を調査してください。【条件】売買物件のみ（賃貸は除外）・2000万円以内・以下のエリア限定：(1) 黒磯駅から半径1km以内(2) 那須塩原駅から半径1km以内【1】空きビル・空き店舗・空き家の売買物件：(a) 旅館業・宿泊施設に転用できそうな物件(b) 飲食・物販・フィットネスに転用できそうな物件(c) 物件名・価格・広さ・築年数・問い合わせ先・URL(d) SUUMO・アットホーム・HOME'S等の掲載情報【2】一物四価（不動産価格指標）黒磯・那須塩原エリアの最新情報と過去との比較：(a) 公示地価：最新値と前年比(b) 基準地価：最新値と前年比(c) 相続税路線価：最新値と前年比(d) 実勢価格：最近の取引事例(e) 総合判断：今が買い時か・待つべきか出力：冒頭【不動産レポート】{today} 絵文字使用・各項目3行以内・600文字以内・ですます調・最後に今週のアクション1つ"
CATEGORY = '不動産'

def main():
    today = datetime.now().strftime('%Y/%m/%d')
    log_activity('システム自動実行', 'agent', '不動産エージェント')
    print('不動産エージェント実行中...')
    p = PROMPT.replace('{today}', today)
    report_raw = client.messages.create(tools=[{"type":"web_search_20250305","name":"web_search"}], model='claude-sonnet-4-5', max_tokens=1500,
        messages=[{'role': 'user', 'content': p}])
    full_text = ''
    for block in report_raw.content:
        if hasattr(block, 'text'):
            full_text += block.text
    report = full_text
    print(report)
    save_report('fudosan', report)
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