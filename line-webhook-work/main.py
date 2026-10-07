# -*- coding: utf-8 -*-
"""
みさきちゃん LINE アシスタント / メイン処理
"""

import os
import time
import json
import hashlib
import hmac
import base64
import uuid
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timedelta, timezone

LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET", "")
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
COACH_LINE_USER_ID = os.environ.get("COACH_LINE_USER_ID", "")
REVIEWER_LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("REVIEWER_LINE_CHANNEL_ACCESS_TOKEN", "")
# v2.1 ステートレストークン方式（同一チャネルを他システムと共用しても互いを無効化しない）
# 未設定ならREVIEWER_LINE_CHANNEL_ACCESS_TOKEN（v1固定トークン）にフォールバックする
REVIEWER_LINE_JWT_PRIVATE_KEY_B64 = os.environ.get("REVIEWER_LINE_JWT_PRIVATE_KEY_B64", "")
REVIEWER_LINE_JWT_PRIVATE_KEY = (
    base64.b64decode(REVIEWER_LINE_JWT_PRIVATE_KEY_B64).decode("utf-8")
    if REVIEWER_LINE_JWT_PRIVATE_KEY_B64 else ""
)
REVIEWER_LINE_JWT_KID = os.environ.get("REVIEWER_LINE_JWT_KID", "")
REVIEWER_CHANNEL_ID = os.environ.get("REVIEWER_CHANNEL_ID", "")
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "")

from client_config import build_system_prompt

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"
LINE_TOKEN_URL = "https://api.line.me/oauth2/v3/token"
LINE_CONTENT_URL = "https://api-data.line.me/v2/bot/message/{}/content"
JST = timezone(timedelta(hours=9))

CLIENT_NAME = "みさきちゃん"
TARGET_WEIGHT = 57.5
MAINTENANCE_PERIODS = [
    {"start": "2026-06-17", "end": "2026-06-22", "label": "メンテ①"},
    {"start": "2026-07-03", "end": "2026-07-09", "label": "メンテ②"},
    {"start": "2026-07-21", "end": "2026-07-27", "label": "メンテ③"},
]


def verify_line_signature(body: bytes, signature: str) -> bool:
    if not LINE_CHANNEL_SECRET or not signature:
        return False
    mac = hmac.new(LINE_CHANNEL_SECRET.encode("utf-8"), body, hashlib.sha256)
    expected = base64.b64encode(mac.digest()).decode("utf-8")
    return hmac.compare_digest(expected, signature)


def _call_claude(model: str, system: str, user_content: str, max_tokens: int) -> str:
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": user_content}],
    }
    if system:
        payload["system"] = system
    req = urllib.request.Request(
        ANTHROPIC_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as res:
        data = json.loads(res.read().decode("utf-8"))
    parts = [b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"]
    return "\n".join(parts).strip()


def extract_record(client_message: str) -> dict:
    """みさきちゃんのメッセージから体重・体脂肪率・摂取カロリーを抽出する。
    抽出できなければ全項目 null を返す。"""
    today_jst = datetime.now(JST).strftime("%Y-%m-%d")
    prompt = (
        "以下はダイエットクライアントからのLINEメッセージです。\n"
        "体重(kg)・体脂肪率(%)・摂取カロリー(kcal)・日付が本文中に含まれていれば抽出してください。\n"
        f"日付の言及がなければ今日の日付（{today_jst}、JST）を使ってください。\n"
        "含まれていない項目は null にしてください。\n"
        "出力はJSONオブジェクトのみ。説明文は一切不要です。\n"
        '形式: {"date": "YYYY-MM-DD", "weight": number|null, "body_fat": number|null, "kcal": integer|null}\n\n'
        f"--- メッセージ ---\n{client_message}"
    )
    try:
        text = _call_claude("claude-haiku-4-5-20251001", "", prompt, 200)
        text = text.strip().strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
        data = json.loads(text)
        return {
            "date": data.get("date") or today_jst,
            "weight": data.get("weight"),
            "body_fat": data.get("body_fat"),
            "kcal": data.get("kcal"),
        }
    except Exception as e:
        print(f"[extract_record] 抽出失敗（下書き生成は継続）: {e}")
        return {"date": today_jst, "weight": None, "body_fat": None, "kcal": None}


def save_record(record: dict) -> None:
    if record.get("weight") is None and record.get("kcal") is None:
        return
    try:
        from google.cloud import firestore
        db = firestore.Client()
        doc_ref = db.collection("misaki_records").document(record["date"])
        update = {"date": record["date"]}
        if record.get("weight") is not None:
            update["weight"] = record["weight"]
        if record.get("body_fat") is not None:
            update["body_fat"] = record["body_fat"]
        if record.get("kcal") is not None:
            update["kcal"] = record["kcal"]
        update["updated_at"] = firestore.SERVER_TIMESTAMP
        doc_ref.set(update, merge=True)
    except Exception as e:
        print(f"[save_record] Firestore保存失敗（処理は継続）: {e}")


def load_all_records() -> list:
    try:
        from google.cloud import firestore
        db = firestore.Client()
        docs = db.collection("misaki_records").stream()
        records = [d.to_dict() for d in docs]
        records.sort(key=lambda r: r.get("date", ""))
        return records
    except Exception as e:
        print(f"[load_all_records] Firestore読込失敗: {e}")
        return []


def build_current_status_text(records: list) -> str:
    weight_records = [r for r in records if r.get("weight") is not None]
    if not weight_records:
        return "【現在の進行状況】\nまだ体重データの記録がありません。"

    latest = weight_records[-1]
    min_rec = min(weight_records, key=lambda r: r["weight"])
    lines = ["【現在の進行状況】（自動更新）"]
    lines.append(f"- 直近の体重：{latest['date']} {latest['weight']}kg")
    if latest.get("body_fat") is not None:
        lines.append(f"- 直近の体脂肪率：{latest['body_fat']}%")
    lines.append(f"- 最軽量：{min_rec['date']} {min_rec['weight']}kg")
    if TARGET_WEIGHT:
        remain = round(min_rec["weight"] - TARGET_WEIGHT, 1)
        if remain > 0:
            lines.append(f"- 目標まで：あと{remain}kg")
        else:
            lines.append("- 目標体重は達成済み")
    return "\n".join(lines)


def generate_chart_url(records: list) -> str:
    """体重推移グラフを生成してCloud Storageへアップロードし、公開URLを返す。
    失敗時は None（グラフなしで下書きのみ送る）。"""
    weight_records = [r for r in records if r.get("weight") is not None]
    if len(weight_records) < 2 or not GCS_BUCKET_NAME:
        return None
    try:
        from generate_weight_chart import render_weight_chart
        from google.cloud import storage

        data = {
            "client_name": CLIENT_NAME,
            "target_weight": TARGET_WEIGHT,
            "maintenance_periods": MAINTENANCE_PERIODS,
            "records": weight_records,
        }
        out_path = f"/tmp/chart_{uuid.uuid4().hex}.png"
        render_weight_chart(data, out_path)

        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        object_name = f"charts/{uuid.uuid4().hex}.png"
        blob = bucket.blob(object_name)
        blob.upload_from_filename(out_path, content_type="image/png")
        # バケット側でallUsers:objectViewerを付与済みの前提（均一バケットレベルアクセスのためACLは使わない）
        os.remove(out_path)
        return blob.public_url
    except Exception as e:
        print(f"[generate_chart_url] グラフ生成/アップロード失敗（テキストのみ送信）: {e}")
        return None


def generate_draft(client_message: str, current_status: str) -> str:
    prompt = (
        "みさきちゃんから、次のLINEメッセージが届きました。\n"
        "ルールに沿って返信の下書きを作成してください。\n\n"
        f"--- みさきちゃんのメッセージ ---\n{client_message}"
    )
    try:
        result = _call_claude("claude-opus-4-8", build_system_prompt(current_status), prompt, 1500)
        return result or "（下書きの生成に失敗しました）"
    except urllib.error.HTTPError as e:
        return f"（Claude API エラー: {e.code} {e.read().decode('utf-8', 'ignore')[:300]}）"
    except Exception as e:
        return f"（Claude API 呼び出しで例外: {e}）"


def fetch_line_image(message_id: str) -> bytes:
    """受信チャネル（Honey LaRva）のトークンで画像本体を取得する。"""
    req = urllib.request.Request(
        LINE_CONTENT_URL.format(message_id),
        headers={"Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"},
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read()


def generate_draft_for_image(image_bytes: bytes, current_status: str) -> str:
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    payload = {
        "model": "claude-opus-4-8",
        "max_tokens": 1500,
        "system": build_system_prompt(current_status),
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
                {"type": "text", "text": "みさきちゃんから写真（食事など）が届きました。ルールに沿って返信の下書きを作成してください。"},
            ],
        }],
    }
    req = urllib.request.Request(
        ANTHROPIC_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            data = json.loads(res.read().decode("utf-8"))
        parts = [b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"]
        return "\n".join(parts).strip() or "（下書きの生成に失敗しました）"
    except urllib.error.HTTPError as e:
        return f"（Claude API エラー: {e.code} {e.read().decode('utf-8', 'ignore')[:300]}）"
    except Exception as e:
        return f"（Claude API 呼び出しで例外: {e}）"


def upload_photo_to_gcs(image_bytes: bytes) -> str:
    """みさきちゃんの写真をひつじさんへ転送するためCloud Storageへ保存する。失敗時はNone。"""
    if not GCS_BUCKET_NAME:
        return None
    try:
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        object_name = f"meal_photos/{uuid.uuid4().hex}.jpg"
        blob = bucket.blob(object_name)
        blob.upload_from_string(image_bytes, content_type="image/jpeg")
        return blob.public_url
    except Exception as e:
        print(f"[upload_photo_to_gcs] アップロード失敗: {e}")
        return None


def get_reviewer_access_token() -> str:
    """ステートレスチャネルアクセストークン（/oauth2/v3/token）を都度発行する。
    このトークンは発行数に上限がなく失効も不要なため、都度発行して使い捨てる用途に適している
    （このチャネルを共用する他システムとお互いの発行数を気にしなくてよい）。
    秘密鍵未設定時はv1固定トークンにフォールバック。"""
    if not REVIEWER_LINE_JWT_PRIVATE_KEY or not REVIEWER_LINE_JWT_KID or not REVIEWER_CHANNEL_ID:
        return REVIEWER_LINE_CHANNEL_ACCESS_TOKEN
    try:
        import jwt as pyjwt
        now = int(time.time())
        payload = {
            "iss": REVIEWER_CHANNEL_ID,
            "sub": REVIEWER_CHANNEL_ID,
            "aud": "https://api.line.me/",
            "exp": now + 60 * 30,
            "jti": str(uuid.uuid4()),
        }
        assertion = pyjwt.encode(
            payload, REVIEWER_LINE_JWT_PRIVATE_KEY, algorithm="RS256",
            headers={"alg": "RS256", "typ": "JWT", "kid": REVIEWER_LINE_JWT_KID},
        )
        data = urllib.parse.urlencode({
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": assertion,
        }).encode()
        req = urllib.request.Request(LINE_TOKEN_URL, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=15) as res:
            return json.loads(res.read())["access_token"]
    except Exception as e:
        print(f"[get_reviewer_access_token] ステートレストークン発行失敗、v1にフォールバック: {e}")
        return REVIEWER_LINE_CHANNEL_ACCESS_TOKEN


def push_to_coach(text: str, image_url: str = None) -> None:
    chunks = [text[i:i + 4800] for i in range(0, len(text), 4800)] or ["（空）"]
    messages = [{"type": "text", "text": c} for c in chunks[:4]]
    if image_url:
        messages.append({
            "type": "image",
            "originalContentUrl": image_url,
            "previewImageUrl": image_url,
        })
    payload = {"to": COACH_LINE_USER_ID, "messages": messages[:5]}
    req = urllib.request.Request(
        LINE_PUSH_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {get_reviewer_access_token()}",
        },
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as e:
        print(f"[push_to_coach] 送信失敗: {e.code} {e.read().decode('utf-8', 'ignore')[:500]}")
    except Exception as e:
        print(f"[push_to_coach] 送信失敗: {e}")


def already_processed(message_id: str) -> bool:
    """LINEはWebhook応答が遅いと同じメッセージを再送してくる。
    メッセージIDをFirestoreに記録し、二重処理（重複Push・Claude API二重課金）を防ぐ。"""
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

    if not verify_line_signature(body, signature):
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

        if msg_type == "text":
            client_message = msg["text"]

            record = extract_record(client_message)
            save_record(record)

            all_records = load_all_records()
            current_status = build_current_status_text(all_records)
            chart_url = generate_chart_url(all_records)

            draft = generate_draft(client_message, current_status)
            header = (
                "🍀 みさきちゃんから新しいメッセージが届きました\n"
                "──────────────\n"
                f"『{client_message}』\n"
                "──────────────\n\n"
            )
            push_to_coach(header + draft, chart_url)

        elif msg_type == "image":
            try:
                image_bytes = fetch_line_image(message_id)
            except Exception as e:
                print(f"[line_webhook] 画像取得失敗: {e}")
                continue

            all_records = load_all_records()
            current_status = build_current_status_text(all_records)
            draft = generate_draft_for_image(image_bytes, current_status)
            photo_url = upload_photo_to_gcs(image_bytes)
            header = "🍀 みさきちゃんから写真が届きました\n──────────────\n\n"
            push_to_coach(header + draft, photo_url)

    return ("OK", 200)
