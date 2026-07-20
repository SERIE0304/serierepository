import os

def get_line_token():
    # 長期チャネルアクセストークンはGitHub Secrets(LINE_CHANNEL_TOKEN)からのみ取得する。
    # 以前はここでclient_credentialsによる都度新規発行を行っていたが、LINEの
    # 同時有効トークン上限(30個)に達してエラーになる不具合があったため廃止した。
    env_token = os.environ.get('LINE_CHANNEL_TOKEN')
    if not env_token:
        raise RuntimeError('LINE_CHANNEL_TOKEN環境変数が設定されていません（GitHub Secretsを確認してください）')
    return env_token

if __name__ == "__main__":
    print(get_line_token())
