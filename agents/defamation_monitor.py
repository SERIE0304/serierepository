import os, json, anthropic
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

client = anthropic.Anthropic()
from get_line_token import get_line_token
LINE_CHANNEL_TOKEN = get_line_token()
LINE_USER_ID = 'U206a030c1759f1ed8f4c684d03d11915'

MONITOR_ACCOUNTS = ['gorigori_box', 'ci_bxx53']
ALERT_KEYWORDS = ['某元日本チャンピオン', '暴行', '不倫']
EVIDENCE_LOG = os.path.join(os.path.dirname(__file__), 'defamation_evidence.log')

def send_line_message(message):
    import urllib.request
    data = json.dumps({'to': LINE_USER_ID, 'messages': [{'type': 'text', 'text': message}]}).encode('utf-8')
    req = urllib.request.Request('https://api.line.me/v2/bot/message/push', data=data,
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + LINE_CHANNEL_TOKEN})
    urllib.request.urlopen(req)

def save_evidence(account, content, timestamp):
    with open(EVIDENCE_LOG, 'a', encoding='utf-8') as f:
        f.write(f'[{timestamp}] @{account}\n{content}\n{"="*60}\n\n')

def check_account(account, now):
    keywords = '・'.join(ALERT_KEYWORDS)
    prompt = (
        f'今日は{now}です。X（旧Twitter）のアカウント @{account} の直近24時間以内の投稿を検索してください。\n\n'
        f'検索対象キーワード：{keywords}\n\n'
        f'以下の方法で検索してください：\n'
        f'- site:x.com/{account} を検索\n'
        f'- x.com/{account} のページを確認\n\n'
        f'該当する投稿が見つかった場合：\n'
        f'- 投稿の全文\n'
        f'- 投稿日時\n'
        f'- URL（わかる場合）\n'
        f'を日本語で報告してください。\n\n'
        f'直近24時間以内に該当する投稿が見つからなかった場合は、正確に「NO_VIOLATION_FOUND」とだけ返してください。'
    )
    result = client.messages.create(
        model='claude-opus-4-5',
        max_tokens=1000,
        tools=[{'type': 'web_search_20250305', 'name': 'web_search'}],
        messages=[{'role': 'user', 'content': prompt}]
    )
    text = ''
    for block in result.content:
        if hasattr(block, 'text'):
            text += block.text
    return text

def main():
    now = datetime.now().strftime('%Y/%m/%d %H:%M')
    print(f'誹謗中傷監視エージェント起動 {now}')

    violations = []

    for account in MONITOR_ACCOUNTS:
        print(f'@{account} を監視中...')
        result = check_account(account, now)
        print(result)
        if 'NO_VIOLATION_FOUND' not in result:
            violations.append((account, result))
            save_evidence(account, result, now)
            print(f'⚠️ @{account} で該当投稿を検知 → 証拠ログ保存済み')

    if violations:
        alert = f'⚠️【誹謗中傷検知】{now}\n\n'
        for account, content in violations:
            alert += f'■ @{account}\n{content}\n\n'
        alert += '※証拠は defamation_evidence.log に保存済み'
        send_line_message(alert)
        print('LINEアラート送信完了')
    else:
        print('該当投稿なし。送信スキップ。')

if __name__ == '__main__':
    main()
