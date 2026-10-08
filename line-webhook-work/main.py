# -*- coding: utf-8 -*-
"""
レシート受信専用 Webhook（旧: みさきちゃん LINE アシスタント）

2026-10-08: みさきちゃんのオンラインダイエットコース終了に伴い、
ダイエット指導まわりの処理（体重記録・グラフ生成・Claudeへの下書き生成・
ひつじさんへのプッシュ通知）を削除。以前の実装は git 履歴から参照可能。

今はひつじさんチャネル宛の画像（MEGUMIさん等からの領収書）を
receipt_handler.py に委譲するだけのシンプルなWebhook。
"""

import hashlib
import hmac
import base64
import json

from receipt_handler import handle_group_event, RECEIPT_LINE_CHANNEL_SECRET


def verify_line_signature(body: bytes, signature: str, secret: str) -> bool:
    if not secret or not signature:
        return False
    mac = hmac.new(secret.encode("utf-8"), body, hashlib.sha256)
    expected = base64.b64encode(mac.digest()).decode("utf-8")
    return hmac.compare_digest(expected, signature)


def already_processed(message_id: str) -> bool:
    """LINEはWebhook応答が遅いと同じメッセージを再送してくる。
    メッセージIDをFirestoreに記録し、二重処理（重複保存）を防ぐ。"""
    try:
        from google.cloud import firestore
        db = firestore.Client()
        doc_ref = db.collection("processed_line_messages").document(message_id)
        doc_ref.create({"processed_at": firestore.SERVER_TIMESTAMP})
        return False
    except Exception as e:
        if "already exists" in str(e).lower() or "ALREADY_EXISTS" in str(e):
            return True
        print(f"[already_processed] 判定失敗（処理は継続）: {e}")
        return False


def line_webhook(request):
    body = request.get_data()
    signature = request.headers.get("X-Line-Signature", "")

    if not verify_line_signature(body, signature, RECEIPT_LINE_CHANNEL_SECRET):
        return ("signature verification failed", 403)

    try:
        events = json.loads(body.decode("utf-8")).get("events", [])
    except Exception:
        return ("bad request", 400)

    for ev in events:
        msg = ev.get("message", {})
        msg_type = msg.get("type")
        if ev.get("type") != "message" or msg_type not in ("text", "image"):
            continue

        message_id = msg.get("id")
        if message_id and already_processed(message_id):
            continue

        handle_group_event(ev)

    return ("OK", 200)
