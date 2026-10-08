import os
import time
import urllib.request
import urllib.error
from datetime import datetime
from get_line_token import get_line_token

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
LINE_CHANNEL_TOKEN = get_line_token()
LINE_USER_ID = "U206a030c1759f1ed8f4c684d03d11915"

# (agentキー, 表示ラベル)
AGENTS = [
    ("panda", "パンダカステラ販路"),
    ("pricing", "SERIE料金提案"),
    ("sns", "SNS・YouTube台本"),
    ("larva", "Honey LaRva集客"),
    ("hojyokin", "補助金調査"),
    ("fudosan", "不動産調査"),
    ("fc", "Honey LaRva FC化"),
]

REPORT_SEPARATOR = "=" * 50


def send_line_message(message, retries=2):
    import json
    data = json.dumps({"to": LINE_USER_ID, "messages": [{"type": "text", "text": message}]}).encode("utf-8")
    for attempt in range(retries + 1):
        req = urllib.request.Request(
            "https://api.line.me/v2/bot/message/push",
            data=data,
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + LINE_CHANNEL_TOKEN}
        )
        try:
            urllib.request.urlopen(req)
            return
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")
            print(f"LINE送信失敗（{attempt + 1}回目）: HTTP {e.code} {body}")
            if attempt < retries:
                time.sleep(2)
            else:
                raise


def _load_report(agent_key):
    """agents/output/{agent_key}_latest.txt を読み込み、本文だけを返す。無ければNone。"""
    path = os.path.join(OUTPUT_DIR, f"{agent_key}_latest.txt")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    if REPORT_SEPARATOR in raw:
        raw = raw.split(REPORT_SEPARATOR, 1)[1]
    return raw.strip()


def _summarize(label, content):
    """150〜200文字程度に要約する。APIが使えない場合は先頭を抜粋する簡易版にフォールバック。"""
    try:
        import anthropic
        from get_api_key import get_api_key
        client = anthropic.Anthropic(api_key=get_api_key())
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": (
                    f"以下は「{label}」エージェントが作成したレポートです。"
                    "内容を150〜200文字程度の日本語で要約してください。要約文だけを出力し、"
                    "前置きや見出しは付けないでください。\n\n" + content
                )
            }]
        )
        text = "".join(block.text for block in response.content if hasattr(block, "text")).strip()
        if text:
            return text
    except Exception as e:
        print(f"{label}の要約でエラー（簡易抜粋にフォールバック）: {e}")
    return content[:200].strip()


def send_friday_review():
    today = datetime.now().strftime("%Y/%m/%d")
    sections = []
    for key, label in AGENTS:
        content = _load_report(key)
        if not content:
            continue
        summary = _summarize(label, content)
        sections.append(f"【{label}】\n{summary}")

    if not sections:
        msg = "【今週の活動まとめ】" + today + "\n\n今週のレポートはまだありません。"
    else:
        msg = "【今週の活動まとめ】" + today + "\n\n" + "\n\n".join(sections)

    send_line_message(msg)
    print(msg)


if __name__ == "__main__":
    send_friday_review()
