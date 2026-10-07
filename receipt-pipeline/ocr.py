# -*- coding: utf-8 -*-
"""
レシート画像1枚を Claude (Anthropic Messages API) に渡し、
現金出納帳に記帳するための構造化データを抽出する。

main.py の _call_claude() と同じ urllib ベースの素朴な実装にして、
依存ライブラリを増やさない。
"""
import base64
import json
import os
import urllib.error
import urllib.request

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-5"

PROMPT = """あなたは日本の小規模企業（宿泊業・ボクシングジム・移動販売）の経理担当です。
添付したレシート/領収書の写真から、現金出納帳に記帳するための情報を抽出してください。

以下のJSON形式のみを出力してください（説明文は一切不要）:
{
  "date": "YYYY-MM-DD",            // レシートに印字された取引日。今日の日付ではない
  "store": "店名（支店名含む）",
  "items": "購入品の短い要約（例: 消耗品 等）",
  "reg": "登録番号(Tから始まる)。記載なければnull",
  "amount": 1234,                  // 合計金額（整数、円）。斜線・黒塗りで除外されている商品があれば、
                                    // 除外後の金額を計算してamountに入れ、notesにその判断根拠を書くこと
  "category": "消耗品費/食材費/車両費/燃料費/旅費交通費/通信費/事務用品費/広告宣伝費/水道光熱費/修繕費/諸会費/雑費 のいずれか",
  "confidence": "high/medium/low", // low/medium の場合は判断に自信がないケース（黒塗り・斜線・手書きで読み取りにくい等）
  "readable": true,                // レシートとして読み取れたか。レシートでない・金額が全く判読不能ならfalse
  "notes": "判断の根拠や不確実な点があれば記載。なければ空文字"
}
"""


def extract_receipt(image_bytes: bytes) -> dict:
    """失敗時は {"readable": False, "notes": "<エラー内容>"} を返す。"""
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    payload = {
        "model": MODEL,
        "max_tokens": 1000,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
                {"type": "text", "text": PROMPT},
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
        text = "\n".join(parts).strip()
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
        result = json.loads(text)
        return result
    except urllib.error.HTTPError as e:
        return {"readable": False, "notes": f"Claude APIエラー: {e.code} {e.read().decode('utf-8', 'ignore')[:300]}"}
    except Exception as e:
        return {"readable": False, "notes": f"抽出失敗: {e}"}
