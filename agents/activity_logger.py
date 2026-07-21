import json, os
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(__file__), 'activity_log.json')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')

def save_report(agent_name: str, content: str):
    """エージェントのレポートをoutput/に保存する"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = datetime.now().strftime('%Y%m%d_%H%M')
    # 最新版（上書き）
    latest_path = os.path.join(OUTPUT_DIR, f'{agent_name}_latest.txt')
    with open(latest_path, 'w', encoding='utf-8') as f:
        f.write(f'生成日時: {datetime.now().strftime("%Y/%m/%d %H:%M")}\n')
        f.write('='*50 + '\n')
        f.write(content)
    # 日付付きバックアップ
    backup_path = os.path.join(OUTPUT_DIR, f'{agent_name}_{today}.txt')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(f'生成日時: {datetime.now().strftime("%Y/%m/%d %H:%M")}\n')
        f.write('='*50 + '\n')
        f.write(content)
    print(f'レポート保存: {latest_path}')

def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'activities': []}

def save_log(data):
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def log_activity(user: str, action: str, detail: str = ''):
    """誰が・何を・いつ行ったかを記録する"""
    data = load_log()
    data['activities'].append({
        'timestamp': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
        'user': user,
        'action': action,
        'detail': detail
    })
    save_log(data)

def log_chat(user: str, role: str, question: str, answer: str):
    """Leidyチャットの会話を記録する"""
    data = load_log()
    data['activities'].append({
        'timestamp': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
        'user': user,
        'action': 'leidy_chat',
        'role': role,
        'question': question,
        'answer': answer
    })
    save_log(data)

def print_summary():
    """ターミナルで履歴を確認する"""
    data = load_log()
    acts = data.get('activities', [])
    if not acts:
        print('履歴はまだありません。')
        return
    print(f'\n{"="*60}')
    print(f'  活動履歴  （全{len(acts)}件）')
    print(f'{"="*60}')
    for a in reversed(acts[-30:]):
        user = a.get('user', '不明')
        action = a.get('action', '')
        ts = a.get('timestamp', '')
        if action == 'leidy_chat':
            print(f"[{ts}] {user} (チャット) Q: {a.get('question','')[:40]}")
        else:
            print(f"[{ts}] {user} → {action} {a.get('detail','')[:40]}")
    print()

if __name__ == '__main__':
    import sys
    # コマンドライン: python activity_logger.py log "名前" "アクション" "詳細"
    if len(sys.argv) >= 4 and sys.argv[1] == 'log':
        user = sys.argv[2]
        action = sys.argv[3]
        detail = sys.argv[4] if len(sys.argv) >= 5 else ''
        log_activity(user, action, detail)
        print(f'記録しました: [{user}] {action} {detail}')
    else:
        print_summary()
