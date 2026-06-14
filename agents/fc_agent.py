import os, anthropic
from datetime import datetime

client = anthropic.Anthropic()
LINE_CHANNEL_TOKEN = open(os.path.expanduser('~/lodgers/agents/line_token.txt')).read().strip()
LINE_USER_ID = 'U206a030c1759f1ed8f4c684d03d11915'

def send_line_message(message):
    import urllib.request, json
    data = json.dumps({'to': LINE_USER_ID, 'messages': [{'type': 'text', 'text': message}]}).encode('utf-8')
    req = urllib.request.Request('https://api.line.me/v2/bot/message/push', data=data,
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + LINE_CHANNEL_TOKEN})
    urllib.request.urlopen(req)

PROMPT = '今日は{today}です。フィットネスボクシングジムHoney LaRva（栃木県大田原市・那須塩原市直営2店舗）のフランチャイズ化を実現するまでの手順を調査してください。【1】FC本部設立の法的要件（中小小売商業振興法の情報開示書面など）。【2】FC化前に整備すべきもの（マニュアル・収支モデル・研修制度の骨格）。【3】FC化にかかる費用相場（弁護士・中小企業診断士への依頼費用）。【4】フィットネス業界でFC化に成功した小規模ジムの事例。【5】FC化までの現実的なスケジュール（6ヶ月・1年・2年プラン）。【6】相談できる専門家・支援機関（栃木県よろず支援拠点・中小企業診断士など）。今すぐ着手できるアクションを優先して整理してください。出力：冒頭【FC化レポート】{today} 絵文字使用・具体的な手順・費用・連絡先を含む・ですます調'

def main():
    today = datetime.now().strftime('%Y/%m/%d')
    print('FC化エージェント実行中...')
    p = PROMPT.replace('{today}', today)
    report = client.messages.create(model='claude-haiku-4-5-20251001', max_tokens=2000,
        messages=[{'role': 'user', 'content': p}]).content[0].text
    print(report)
    send_line_message(report)
    print('LINE送信完了！')

if __name__ == '__main__': main()