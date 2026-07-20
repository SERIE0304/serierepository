import os
import time
import uuid
import json
import urllib.request
import urllib.parse
import urllib.error

import jwt

CHANNEL_ID = "2010176953"


def get_line_token():
    # ステートレスチャネルアクセストークン(v2.1)を都度発行して使う。
    # 従来の長期トークン(v1)は「同一チャネルで再発行すると既存トークンが即座に無効化される」
    # 仕様のため、このチャネルを共用する他システム(みさきちゃん自動化など)が
    # 独自に再発行するたびに、こちら側のトークンが知らないうちに失効していた。
    # v2.1は複数のトークンを同時発行しても互いを無効化しないため、この問題が起きない。
    private_key = os.environ.get('LINE_JWT_PRIVATE_KEY')
    kid = os.environ.get('LINE_JWT_KID')
    if not private_key or not kid:
        raise RuntimeError('LINE_JWT_PRIVATE_KEY / LINE_JWT_KID 環境変数が設定されていません（GitHub Secretsを確認してください）')

    last_error = None
    for attempt in range(3):
        # jtiを含め毎回アサーションを作り直す。GitHub Actionsの並列ジョブが
        # 同一秒にリクエストすると、jtiなしでは複数ジョブが完全に同一の
        # JWTアサーションを送ることになり、LINE側で衝突して404になる事象を確認したため。
        now = int(time.time())
        payload = {
            "iss": CHANNEL_ID,
            "sub": CHANNEL_ID,
            "aud": "https://api.line.me/",
            "exp": now + 60 * 30,
            "token_exp": 60 * 60 * 24 * 30,
            "jti": str(uuid.uuid4()),
        }
        assertion = jwt.encode(payload, private_key, algorithm="RS256", headers={"alg": "RS256", "typ": "JWT", "kid": kid})
        data = urllib.parse.urlencode({
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": assertion,
        }).encode()

        try:
            req = urllib.request.Request("https://api.line.me/oauth2/v2.1/token", data=data)
            with urllib.request.urlopen(req) as res:
                return json.loads(res.read())["access_token"]
        except urllib.error.URLError as e:
            last_error = e
            print(f'トークン取得失敗（{attempt + 1}回目）: {e}')
            if attempt < 2:
                time.sleep(2)
    raise last_error


if __name__ == "__main__":
    print(get_line_token())
