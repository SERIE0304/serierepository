import os


def get_line_token():
    # 固定のチャネルアクセストークン（LINE Developers Consoleで発行した長期トークン）を使う。
    # 以前はJWTでステートレストークンを都度発行する方式だったが、
    # チャネルに登録した鍵と一致せず/oauth2/v3/tokenが常にHTTP 400を返し、
    # 2026-07-20の導入以降エージェントが一度も送信に成功しない不具合を起こしたため、
    # 固定トークン方式に戻した。
    token = os.environ.get('LINE_CHANNEL_TOKEN')
    if not token:
        raise RuntimeError('LINE_CHANNEL_TOKEN 環境変数が設定されていません（GitHub Secretsを確認してください）')
    return token


if __name__ == "__main__":
    print(get_line_token())
