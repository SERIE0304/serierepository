# -*- coding: utf-8 -*-
"""
ひつじさんチャネル（MEGUMIさん等が1:1チャットで送ってくる画像）を領収書として扱い、
GCSへ保存するだけの軽量ハンドラ。

読み取り（OCR）・現金出納帳への記帳は、意図的にここでは行わない。
ローカルPC側の receipt-pipeline/sync_and_process.py が GCS を定期的に
同期して処理する（Cloud Function側は「受け取って保存するだけ」に留め、
判断ロジックの調整をデプロイなしでローカルで素早く回せるようにするため）。

main.py の既存の1:1チャット（みさきちゃん）向けロジックには一切触れない。
"""

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

# ひつじさんのチャネル（MEGUMIさんが画像を送るグループが所属するチャネル）専用の認証情報。
# みさきちゃんの1:1チャット用チャネル（LINE_CHANNEL_SECRET/LINE_CHANNEL_ACCESS_TOKEN, main.py側）
# とは別チャネルのため、画像取得・返信にはこちらを使う必要がある。
RECEIPT_LINE_CHANNEL_SECRET = os.environ.get("RECEIPT_LINE_CHANNEL_SECRET", "")
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("RECEIPT_LINE_CHANNEL_ACCESS_TOKEN", "")
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "")

# 空文字列なら全員を対象（Phase B で送信者IDを特定するまでの暫定状態）。
# カンマ区切りで複数IDを設定すると、そのIDの送信者の画像だけを保存する。
RECEIPT_ALLOWED_USER_IDS = {
    uid.strip() for uid in os.environ.get("RECEIPT_ALLOWED_USER_IDS", "").split(",") if uid.strip()
}
# 設定されていれば、そのgroupId以外のグループ/ルームは無視する（任意）。
RECEIPT_GROUP_ID = os.environ.get("RECEIPT_GROUP_ID", "")

LINE_CONTENT_URL = "https://api-data.line.me/v2/bot/message/{}/content"
LINE_REPLY_URL = "https://api.line.me/v2/bot/message/reply"
LINE_GROUP_MEMBER_URL = "https://api.line.me/v2/bot/group/{}/member/{}"
LINE_PROFILE_URL = "https://api.line.me/v2/bot/profile/{}"
JST = timezone(timedelta(hours=9))


def fetch_line_image(message_id: str) -> bytes:
    """main.py の同名関数と同じ実装（循環import回避のためここにも持つ）。"""
    req = urllib.request.Request(
        LINE_CONTENT_URL.format(message_id),
        headers={"Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"},
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read()


def get_display_name(group_id: str, user_id: str) -> str:
    """送信者の表示名を取得する。MEGUMIさん特定のためログに出すだけの用途。失敗時は空文字。
    グループ/ルーム内なら group member API、1:1チャットなら profile API を使う。"""
    if not user_id:
        return ""
    url = LINE_GROUP_MEMBER_URL.format(group_id, user_id) if group_id else LINE_PROFILE_URL.format(user_id)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"})
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            data = json.loads(res.read().decode("utf-8"))
        return data.get("displayName", "")
    except Exception as e:
        print(f"[get_display_name] 取得失敗: {e}")
        return ""


def upload_receipt_to_gcs(image_bytes: bytes, user_id: str) -> str:
    """領収書画像を GCS の receipts/ 配下へ保存する。失敗時は None。"""
    if not GCS_BUCKET_NAME:
        print("[upload_receipt_to_gcs] GCS_BUCKET_NAME 未設定のため保存をスキップ")
        return None
    try:
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        ts = datetime.now(JST).strftime("%Y%m%d_%H%M%S")
        suffix = (user_id or "unknown")[-6:]
        object_name = f"receipts/{ts}_{suffix}.jpg"
        blob = bucket.blob(object_name)
        blob.upload_from_string(image_bytes, content_type="image/jpeg")
        return object_name
    except Exception as e:
        print(f"[upload_receipt_to_gcs] アップロード失敗: {e}")
        return None


def reply_message(reply_token: str, text: str) -> None:
    if not reply_token:
        return
    payload = {"replyToken": reply_token, "messages": [{"type": "text", "text": text}]}
    req = urllib.request.Request(
        LINE_REPLY_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        },
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=15)
    except urllib.error.HTTPError as e:
        print(f"[reply_message] 送信失敗: {e.code} {e.read().decode('utf-8', 'ignore')[:300]}")
    except Exception as e:
        print(f"[reply_message] 送信失敗: {e}")


def handle_group_event(ev: dict) -> None:
    """ひつじさんチャネルから届いたイベントを処理する（1:1チャット・グループ/ルームいずれも対象）。
    例外は内部で握りつぶし、呼び出し元は継続する。"""
    try:
        msg = ev.get("message", {})
        if ev.get("type") != "message":
            return
        msg_type = msg.get("type")

        if msg_type == "text":
            # 社員（小筆さん想定）からの日々の進捗報告はここで画像と分岐し、
            # progress_handler.py に委譲する（次の指示をClaudeに生成させて返信する）。
            from progress_handler import handle_text_event
            handle_text_event(ev)
            return

        if msg_type != "image":
            return  # テキスト・画像以外は今は何もしない

        source = ev.get("source", {})
        group_id = source.get("groupId") or source.get("roomId") or ""
        user_id = source.get("userId", "")

        if RECEIPT_GROUP_ID and group_id and group_id != RECEIPT_GROUP_ID:
            print(f"[handle_group_event] 対象外のgroupId: {group_id}")
            return

        display_name = get_display_name(group_id, user_id)
        print(f"[handle_group_event] 画像受信 userId={user_id} displayName={display_name!r} groupId={group_id or '(1:1チャット)'}")

        if RECEIPT_ALLOWED_USER_IDS and user_id not in RECEIPT_ALLOWED_USER_IDS:
            print(f"[handle_group_event] 許可リスト外のため保存スキップ: userId={user_id}")
            return

        message_id = msg.get("id")
        if not message_id:
            return
        image_bytes = fetch_line_image(message_id)
        object_name = upload_receipt_to_gcs(image_bytes, user_id)

        if object_name:
            reply_message(ev.get("replyToken", ""), "📥 レシートを保存しました")
        else:
            print(f"[handle_group_event] GCS保存に失敗したため返信は送らない: message_id={message_id}")
    except Exception as e:
        print(f"[handle_group_event] 予期しないエラー（処理は継続）: {e}")
