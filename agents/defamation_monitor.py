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

def save_evidence(account, content, reason, timestamp):
    with open(EVIDENCE_LOG, 'a', encoding='utf-8') as f:
        f.write(f'[{timestamp}] @{account} 【検知理由: {reason}】\n{content}\n{"="*60}\n\n')

def check_account(account, now):
    keywords_str = '・'.join(ALERT_KEYWORDS)
    prompt = (
        f'今日は{now}です。X（旧Twitter）のアカウント @{account} の直近24時間以内の投稿を検索してください。\n\n'
        f'【検索方法】\n'
        f'- site:x.com/{account} で検索\n'
        f'- x.com/{account} のページを確認\n\n'
        f'【報告対象①：キーワード検知】\n'
        f'以下のキーワードを含む投稿：{keywords_str}\n\n'
        f'【報告対象②：AI判断による法的リスク投稿】\n'
        f'キーワードに関係なく、以下に該当する可能性がある投稿をすべて報告：\n'
        f'- 誹謗中傷・名誉毀損（特定の人物を傷つける内容）\n'
        f'- 侮辱・罵倒（人格否定、差別的表現）\n'
        f'- 脅迫・恫喝（「〜してやる」「〜させる」などの威圧）\n'
        f'- 虚偽の事実の拡散（嘘の情報を事実として述べる）\n'
        f'- プライバシー侵害（住所・電話番号・家族情報などの暴露）\n'
        f'- ハラスメント（執拗な攻撃・嫌がらせ）\n\n'
        f'【出力形式】\n'
        f'該当投稿が見つかった場合、以下を報告：\n'
        f'- 投稿の全文\n'
        f'- 投稿日時\n'
        f'- URL（わかる場合）\n'
        f'- 検知理由（キーワード検知 or AI判断：該当カテゴリ名）\n\n'
        f'直近24時間以内に該当投稿が一切ない場合のみ「NO_VIOLATION_FOUND」と返してください。'
    )
    result = client.messages.create(
        model='claude-opus-4-5',
        max_tokens=1500,
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
        account_not_found = any(phrase in result for phrase in [
            'アカウントが存在しない', '確認できませんでした', 'アカウントは見つかりません',
            'not found', 'does not exist', 'account not found'
        ])
        if 'NO_VIOLATION_FOUND' not in result and not account_not_found:
            violations.append((account, result))
            save_evidence(account, result, 'キーワード+AI判断', now)
            print(f'⚠️ @{account} で該当投稿を検知 → 証拠ログ保存済み')
        elif account_not_found:
            print(f'⚠️ @{account} アカウントが見つかりません。アカウント名を確認してください。')

    if violations:
        alert = f'⚠️【誹謗中傷検知アラート】{now}\n\n'
        for account, content in violations:
            alert += f'■ @{account}\n{content}\n\n'
        alert += '※証拠は defamation_evidence.log に自動保存済み'
        send_line_message(alert)
        print('LINEアラート送信完了')
    else:
        print('該当投稿なし。送信スキップ。')

if __name__ == '__main__':
    main()
