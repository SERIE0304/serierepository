from flask import Flask, request, jsonify
import json, os, anthropic, urllib.request, threading
from get_line_token import get_line_token

app = Flask(__name__)

LINE_CHANNEL_TOKEN = get_line_token()
LINE_USER_ID = 'U206a030c1759f1ed8f4c684d03d11915'
REPORT_CACHE = os.path.expanduser('~/lodgers/agents/hojyokin_last_report.json')
DOCS_OUTPUT = os.path.expanduser('~/lodgers/agents/hojyokin_draft_docs.txt')

client = anthropic.Anthropic()

COMPANY_PROFILE = """
【申請事業者情報】
・会社名：株式会社芹江コンチェルト
・代表者：芹江匡晋（元プロボクシング日本スーパーバンタム級第35代チャンピオン）
・所在地：栃木県那須塩原市黒磯（JR黒磯駅近く）
・従業員数：少数精鋭（小規模事業者）
・事業①：Lodgers Bldg SERIE（旅館業・簡易宿所・民泊）/ 6,000円〜/泊 / Booking.com・Airbnb・VRBO運営 / インバウンド対応
・事業②：パンダベビーカステラ（キッチンカー・食品販売・マルシェ出店・地域物産）
・事業③：Honey LaRva（フィットネスボクシングジム / 大田原市・那須塩原市の直営2店舗 / 自治体健康事業連携検討中）
・地域特性：那須塩原市は観光地（那須高原）と農業・移住促進エリア / 黒磯駅周辺は再開発・空き家活用が課題
・強み：元チャンピオンのブランド力・地域密着・3事業によるシナジー・観光×健康×食のユニークな組み合わせ
"""

def send_line_message(message):
    data = json.dumps({'to': LINE_USER_ID, 'messages': [{'type': 'text', 'text': message}]}).encode('utf-8')
    req = urllib.request.Request('https://api.line.me/v2/bot/message/push', data=data,
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + LINE_CHANNEL_TOKEN})
    urllib.request.urlopen(req)

def web_search_run(messages):
    """Web検索ツール付きでClaudeを呼び出し、最終テキストを返す"""
    result = ''
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
                result = block.text
            if block.type == 'tool_use':
                tool_results.append({'type': 'tool_result', 'tool_use_id': block.id, 'content': '検索完了'})
        if response.stop_reason == 'end_turn':
            break
        if tool_results:
            messages.append({'role': 'user', 'content': tool_results})
    return result

def search_adoption_cases(subsidy_name):
    """各補助金の採択事例・採択されやすいポイントを調査"""
    prompt = f'''「{subsidy_name}」の採択事例と採択されやすい申請書の書き方を調査してください。

以下を検索して具体的に報告してください：
1. 採択された事業者の事例（業種・事業内容・採択理由）
2. 採択率が高い申請書に共通するポイント（審査員が重視する項目）
3. 旅館・宿泊業・フィットネス・飲食・キッチンカー業種での採択事例
4. 不採択になりやすいNGパターン
5. 加点されやすい要素（地域貢献・雇用・デジタル化・女性活躍など）

採択事例は「{subsidy_name} 採択事例」「{subsidy_name} 採択された 事業内容」で検索してください。
採択されやすいポイントは「{subsidy_name} 採択のコツ」「{subsidy_name} 審査ポイント」で検索してください。'''

    return web_search_run([{'role': 'user', 'content': prompt}])

def generate_application_drafts(report_text):
    """採択事例を調査した上で、採択されやすい申請書下書きを生成"""

    # Step1: レポートから補助金名を抽出
    extract_resp = client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=500,
        messages=[{'role': 'user', 'content': f'以下の補助金レポートから補助金名を全て抽出してください。補助金名のみをカンマ区切りで出力してください。\n\n{report_text}'}]
    )
    subsidy_names_raw = extract_resp.content[0].text.strip()
    subsidy_names = [s.strip() for s in subsidy_names_raw.split(',') if s.strip()][:5]  # 最大5件

    send_line_message(f'🔍 採択事例を調査中...\n対象補助金：{len(subsidy_names)}件\n少々お待ちください⏳')

    # Step2: 各補助金の採択事例を調査
    adoption_cases = {}
    for name in subsidy_names:
        send_line_message(f'📚 「{name}」の採択事例を調査中...')
        cases = search_adoption_cases(name)
        adoption_cases[name] = cases

    send_line_message('✏️ 採択事例をもとに申請書の下書きを作成中...')

    # Step3: 採択事例を踏まえた申請書下書き生成
    cases_summary = '\n\n'.join([f'【{name}の採択事例・採択ポイント】\n{cases}' for name, cases in adoption_cases.items()])

    prompt = f'''あなたは補助金申請の専門家（中小企業診断士）です。
以下の【採択事例・採択ポイント】を徹底的に分析し、採択されやすい申請書の下書きを作成してください。

{COMPANY_PROFILE}

【補助金レポート（申請対象）】
{report_text}

【採択事例・採択ポイント（調査結果）】
{cases_summary}

━━━━━━━━━━━━━━━━━━━━
【重要な指示】
- 採択事例で共通する「審査員が評価するフレーズ・表現」を積極的に使用
- 不採択になりやすいNGパターンを必ず避ける
- 芹江コンチェルトの強み（元チャンピオン×地域密着×3事業シナジー×黒磯駅前立地）を採択ポイントと結びつける
- 加点要素（地域貢献・雇用創出・観光振興・健康増進・デジタル化）を積極的に盛り込む
- 審査員が「ぜひ採択したい」と思う説得力ある文章にする

各補助金について以下の形式で出力：

📋【補助金名】
💡 採択のカギ（この補助金で採択されるための最重要ポイント2〜3点）

■ 事業概要（申請書記載用・200字）
→ 採択事例の表現を参考にした完成文

■ 補助事業の必要性・目的（200字）
→ 審査員が評価する切り口で書いた完成文

■ 期待される効果・波及効果（150字）
→ 数値目標・地域への波及を含めた完成文

■ 事業スケジュール
→ 現実的かつ審査員が安心する月別計画

■ 補助対象経費の内訳（例）
→ 採択率の高い費目構成

■ 加点要素のアピール
→ この申請書に盛り込むべき加点ポイント

■ 審査員へのワンポイント
→ この補助金で特に差がつく記載のコツ

━━━━━━━━━━━━━━━━━━━━
ですます調。採択事例の言い回しを活かした説得力ある文章で。'''

    response = client.messages.create(
        model='claude-sonnet-4-6',
        max_tokens=5000,
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response.content[0].text

def split_and_send(message, chunk_size=4000):
    lines = message.split('\n')
    current = ''
    part = 1
    for line in lines:
        if len(current) + len(line) + 1 > chunk_size:
            send_line_message(f'（{part}）\n' + current.strip())
            current = ''
            part += 1
        current += line + '\n'
    if current.strip():
        send_line_message(f'（{part}）\n' + current.strip())

def handle_apply_yes():
    send_line_message('📂 申請書類の下書きを作成しています...\n\n【処理の流れ】\n① 各補助金の採択事例を調査\n② 採択されやすいポイントを分析\n③ あなたの強みと結びつけて下書き作成\n\n10〜15分ほどかかります⏳')

    if not os.path.exists(REPORT_CACHE):
        send_line_message('⚠️ 補助金レポートのキャッシュがありません。先に補助金エージェントを実行してください。')
        return

    with open(REPORT_CACHE, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    report_text = cache.get('report', '')
    updated = cache.get('updated', '')

    if not report_text:
        send_line_message('⚠️ 直近の補助金レポートが見つかりませんでした。先に補助金エージェントを実行してください。')
        return

    docs = generate_application_drafts(report_text)

    with open(DOCS_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(f'申請書類下書き生成日時: {updated}\n\n')
        f.write(docs)

    send_line_message(f'✅ 採択事例ベースの申請書下書きが完成しました！\n（ベース：{updated}のレポート）\n\n採択された事業者の表現・審査ポイントを反映しています👇')
    split_and_send(docs)
    send_line_message('📌 この下書きをそのまま申請書にコピー＆ペーストしてご利用ください。\n修正・追記・特定の補助金だけ作り直すなど、気軽に声をかけてください！')

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(json.dumps(data, indent=2, ensure_ascii=False))
    for event in data.get('events', []):
        user_id = event.get('source', {}).get('userId', 'なし')
        print(f'\n★★★ User ID: {user_id} ★★★\n')
        if event.get('type') == 'message' and event['message'].get('type') == 'text':
            text = event['message']['text'].strip()
            if text == 'hojyokin_apply:はい':
                threading.Thread(target=handle_apply_yes).start()
            elif text == 'hojyokin_apply:いいえ':
                send_line_message('👍 分かりました！必要な時はいつでも声をかけてください。')
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(port=8080)
