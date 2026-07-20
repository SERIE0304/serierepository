import os, json, anthropic
from datetime import datetime

from get_api_key import get_api_key
client = anthropic.Anthropic(api_key=get_api_key())
from get_line_token import get_line_token
LINE_CHANNEL_TOKEN = get_line_token()
LINE_USER_ID = 'U206a030c1759f1ed8f4c684d03d11915'

def send_line_message(message, retries=2):
    import urllib.request, urllib.error, time
    data = json.dumps({'to': LINE_USER_ID, 'messages': [{'type': 'text', 'text': message}]}).encode('utf-8')
    for attempt in range(retries + 1):
        req = urllib.request.Request('https://api.line.me/v2/bot/message/push', data=data,
            headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + LINE_CHANNEL_TOKEN})
        try:
            urllib.request.urlopen(req)
            return
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors='replace')
            print(f'LINE送信失敗（{attempt + 1}回目）: HTTP {e.code} {body}')
            if attempt < retries:
                time.sleep(2)
            else:
                raise

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

def search_scandal_news():
    now = datetime.now()
    today = now.strftime('%Y/%m/%d %H:%M')
    prompt = (
        'Today is ' + today + '. Search the web (Japanese and English sources) for news from the last 7 days about:\n'
        '- ボクシングの計量オーバー・計量失敗（missed weight, overweight at weigh-in）\n'
        '- 減量失敗・過酷な減量によるトラブル・脱水・入院など（weight cut failures/health issues）\n'
        '- ボクシング界の不都合な真実・スキャンダル・疑惑（judging controversies, doping, unfair matchmaking, '
        'promoter/団体側の問題など）\n'
        '- 格闘技界（MMA・キックボクシング等）における同様の不都合・スキャンダル\n'
        'IMPORTANT: If there is no relevant news in the last 7 days, reply with exactly: NO_NEWS_TODAY\n'
        'If there is news, list each item briefly in Japanese: [出来事の概要] / [情報源・媒体] / [日付]。'
        '複数件あれば箇条書きで。合計800文字以内。'
    )
    report = client.messages.create(
        model='claude-opus-4-5',
        max_tokens=1500,
        tools=[{'type': 'web_search_20250305', 'name': 'web_search'}],
        messages=[{'role': 'user', 'content': prompt}]
    )
    result = ''
    for block in report.content:
        if hasattr(block, 'text'): result += block.text
    return result

def generate_x_drafts(news):
    prompt = (
        'あなたは元プロボクシング日本スーパーバンタム級35代チャンピオン・芹江匡晋（せりえまさあき）本人になりきって、'
        'X（旧Twitter）の投稿文の下書きを作成してください。\n'
        '文体：本音・強気・歯に衣着せぬ・元チャンプ目線での説得力・多少煽り気味だが下品にはならない。'
        '断定調で言い切る（例：「〜だろ」「〜だよ」「〜だと思うね」）。\n'
        'ルール：\n'
        '- 1投稿あたり全角120文字以内（絵文字・ハッシュタグ含む）\n'
        '- ハッシュタグは1〜2個まで\n'
        '- 事実の断定はせず、あくまで芹江さん個人の意見・感想として書く（名誉毀損・断定的な非難を避ける）\n'
        '- 2〜3案作成し、【案1】【案2】【案3】の形式で分ける\n\n'
        '以下のニュースを元に投稿ドラフトを作成してください。\n\n' + news
    )
    response = client.messages.create(
        model='claude-opus-4-5',
        max_tokens=1500,
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response.content[0].text

def run_x_drafts():
    print('Xポスト下書きエージェント running...')
    news = search_scandal_news()
    print(news)
    if 'NO_NEWS_TODAY' in news:
        print('該当ニュースなし。送信スキップ。')
        return
    drafts = generate_x_drafts(news)
    message = (
        '🥊【Xポスト下書き】計量オーバー／減量失敗／ボクシング界・格闘技界の不都合\n'
        + '='*20 + '\n'
        + '元ネタ：\n' + news + '\n\n'
        + '-'*20 + '\n'
        + drafts + '\n\n'
        + '※内容を確認のうえ、そのまま投稿するか編集してからXへ投稿してください。'
    )
    send_line_message(message)
    print('LINE送信完了！')

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'x':
        run_x_drafts()
    else:
        main()
