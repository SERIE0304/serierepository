import os, json, anthropic
from datetime import datetime

client = anthropic.Anthropic()
from get_line_token import get_line_token
LINE_CHANNEL_TOKEN = get_line_token()
LINE_USER_ID = 'U206a030c1759f1ed8f4c684d03d11915'

def send_line_message(message):
    import urllib.request
    data = json.dumps({'to': LINE_USER_ID, 'messages': [{'type': 'text', 'text': message}]}).encode('utf-8')
    req = urllib.request.Request('https://api.line.me/v2/bot/message/push', data=data,
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + LINE_CHANNEL_TOKEN})
    urllib.request.urlopen(req)

def generate_script(news):
    prompt = (
        'あなたはYouTubeチャンネル【芹江案件チャンネル】の台本ライターです。'
        '元プロボクシング日本スーパーバンタム級35代チャンピオン・芹江匡晋さんの'
        '顔出しトーク（一人語り）スタイルで台本を書いてください。'
        'スタイル：テンポ速め・強気・本音・挑発的・エンタメ要素あり・7分以内。'
        '構成：①掴みのひと言（30秒）②ニュース解説（1分）'
        '③元チャンプの視点・本音（3分）④Honey LaRvaジムへの絡み（1分30秒）'
        '⑤クロージング・チャンネル登録促進（30秒）'
        '以下のニュースを元に台本を作成してください。\n\n' + news
    )
    response = client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=2000,
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response.content[0].text

def main():
    now = datetime.now()
    today = now.strftime('%Y/%m/%d %H:%M')
    hour = now.hour
    if hour < 12: time_label = 'Morning'
    elif hour < 17: time_label = 'Afternoon'
    else: time_label = 'Evening'
    prompt = (
        'Today is ' + today + '. Search the web for the latest boxing and martial arts news in Japanese. '
        'PRIORITY: Weight/weigh-in issues - missed weight, overweight, weight cut failures, dehydration. '
        'Also include: recent fight results (last 48hrs), Japanese fighters, world title matches. '
        'IMPORTANT: If there is NO news about weight/weigh-in issues in the last 48 hours, '
        'reply with exactly: NO_NEWS_TODAY '
        'If there IS news, format in Japanese starting with [boxing news] ' + today + '. Emojis, max 3 lines each, 600 chars total.'
    )
    print('Boxing news agent running (' + time_label + ')...')
    report = client.messages.create(
        model='claude-opus-4-5',
        max_tokens=1500,
        tools=[{'type': 'web_search_20250305', 'name': 'web_search'}],
        messages=[{'role': 'user', 'content': prompt}]
    )
    result = ''
    for block in report.content:
        if hasattr(block, 'text'): result += block.text
    print(result)
    if 'NO_NEWS_TODAY' in result:
        print('該当ニュースなし。送信スキップ。')
        return
    send_line_message(result)
    print('LINEニュース送信完了！')
    print('YouTube台本生成中...')
    script = generate_script(result)
    script_message = '\n📝【YouTube台本】\n' + '='*20 + '\n' + script
    send_line_message(script_message)
    print('LINE台本送信完了！')

if __name__ == '__main__': main()
