import os, json, re, anthropic
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

def send_line_image(image_url, preview_url=None):
    import urllib.request
    if not preview_url:
        preview_url = image_url
    data = json.dumps({
        'to': LINE_USER_ID,
        'messages': [{'type': 'image', 'originalContentUrl': image_url, 'previewImageUrl': preview_url}]
    }).encode('utf-8')
    req = urllib.request.Request('https://api.line.me/v2/bot/message/push', data=data,
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + LINE_CHANNEL_TOKEN})
    try:
        urllib.request.urlopen(req)
        return True
    except Exception as e:
        print(f'画像送信エラー: {e}')
        return False

def save_task(cat, task_text):
    data = {'tasks': []}
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r', encoding='utf-8') as f: data = json.load(f)
    data['tasks'].append({'category': cat, 'task': task_text, 'done': False,
        'added': datetime.now().strftime('%Y/%m/%d'), 'week': datetime.now().strftime('%Y-W%W')})
    with open(TASKS_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=2)

PROMPT = """今日は{today}です。栃木県那須塩原市の不動産売買物件情報を調査してください。
【条件】売買物件のみ（賃貸は除外）・2000万円以内・エリア：(1)黒磯駅から半径1km以内 (2)那須塩原駅から半径1km以内

【1】物件情報収集（以下すべて検索）
- SUUMO・アットホーム・HOME'S
- 家いちば（ie-ichiba.net）※空き家・古民家の売買専門サイト
- レインズ・マーケット・インフォメーション（reins.or.jp）※過去取引情報
転用候補：旅館業・宿泊・飲食・物販・フィットネス
各物件の取得項目：物件名・価格・広さ・築年数・掲載元・物件URL・物件画像の直接URL

【2】一物四価（黒磯・那須塩原エリア）
(a) 公示地価：最新値と前年比 (b) 基準地価：最新値と前年比
(c) 相続税路線価：最新値と前年比 (d) 実勢価格：最近の取引事例
(e) 総合判断：今が買い時か・待つべきか

必ず以下のJSON形式のみで返してください（前後に余分なテキスト不要）：
{
  "report": "【不動産レポート】{today}\n絵文字あり・600文字以内・ですます調・最後に今週のアクション1つ",
  "properties": [
    {
      "name": "物件名",
      "price": "価格",
      "area": "広さ",
      "age": "築年数",
      "source": "掲載元（家いちば/レインズ/SUUMO等）",
      "url": "物件ページURL",
      "image_url": "物件画像の直接URL（https://〜.jpg or .png）",
      "reason": "ピックアップ理由1行"
    }
  ]
}"""

CATEGORY = '不動産'

def extract_json(text):
    # コードブロック内のJSONを優先して抽出
    code_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', text)
    if code_match:
        try:
            return json.loads(code_match.group(1))
        except Exception:
            pass
    # 最外殻の{}を抽出
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return None

def main():
    today = datetime.now().strftime('%Y/%m/%d')
    print('不動産エージェント実行中...')
    p = PROMPT.replace('{today}', today)
    report_raw = client.messages.create(
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        model='claude-sonnet-4-5',
        max_tokens=2000,
        messages=[{'role': 'user', 'content': p}]
    )

    full_text = ''
    for block in report_raw.content:
        if hasattr(block, 'text'):
            full_text += block.text
    print(full_text)

    # JSON解析
    data = extract_json(full_text)
    if data:
        report = data.get('report', full_text)
        properties = data.get('properties', [])
    else:
        report = full_text
        properties = []

    # テキストレポートをLINE送信
    send_line_message(report)
    print('LINE送信完了！')

    # ピックアップ物件の詳細＋写真をLINE送信
    sent_count = 0
    for prop in properties:
        caption = (
            f"📍 {prop.get('name', '物件')}\n"
            f"💰 {prop.get('price', '')}\n"
            f"📐 {prop.get('area', '')}　🏚 築{prop.get('age', '')}\n"
            f"📌 {prop.get('source', '')}　{prop.get('reason', '')}\n"
            f"🔗 {prop.get('url', '')}"
        )
        send_line_message(caption)

        img_url = prop.get('image_url', '')
        if img_url and img_url.startswith('https://'):
            ok = send_line_image(img_url)
            if ok:
                sent_count += 1
                print(f'写真送信：{prop.get("name", "")}')
            else:
                print(f'写真取得失敗：{prop.get("name", "")}')
        else:
            print(f'画像URLなし：{prop.get("name", "")}')

    print(f'ピックアップ物件：{len(properties)}件、写真送信：{sent_count}件')

    # タスク抽出
    task_res = client.messages.create(model='claude-haiku-4-5-20251001', max_tokens=100,
        messages=[{'role': 'user', 'content': '以下から今週やるべきアクションを1行で抽出:' + report}])
    task_text = ''
    for block in task_res.content:
        if hasattr(block, 'text'):
            task_text += block.text
    print('タスク：' + task_text.strip())
    # save_task(CATEGORY, task_text.strip())

if __name__ == '__main__': main()
