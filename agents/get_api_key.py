import os

KEY_FILE = os.path.expanduser('~/lodgers/agents/anthropic_key.txt')

def get_api_key():
    key = os.environ.get('ANTHROPIC_API_KEY')
    if key:
        return key
    if os.path.exists(KEY_FILE):
        return open(KEY_FILE).read().strip()
    raise RuntimeError(
        'ANTHROPIC_API_KEY が見つかりません。環境変数を設定するか、'
        + KEY_FILE + ' にAPIキーを1行だけ書いて保存してください。'
    )

if __name__ == '__main__':
    print('OK: APIキーを読み込めました' if get_api_key() else 'NG')
