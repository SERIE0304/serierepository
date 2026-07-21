import os
import urllib.request
import urllib.parse
import json

def get_line_token():
    # GitHub Actionsのsecrets.LINE_CHANNEL_TOKEN（長期チャネルアクセストークン）があればそれを使う。
    # 未設定時のみ、クライアントクレデンシャルで都度トークンを新規発行する（LINEはチャネルあたり
    # 同時に有効なトークンを30個までしか許可しないため、毎回発行すると数週間で上限に達して失敗する）。
    env_token = os.environ.get('LINE_CHANNEL_TOKEN')
    if env_token:
        return env_token
    channel_id = "2010176953"
    channel_secret = "0e1574309fde7cc8bc35d7493b5f921c"
    url = "https://api.line.me/v2/oauth/accessToken"
    data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": channel_id,
        "client_secret": channel_secret
    }).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read())["access_token"]

if __name__ == "__main__":
    print(get_line_token())
