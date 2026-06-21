import os
import re
import json
import urllib.request
from datetime import datetime, timedelta, timezone

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from get_line_token import get_line_token

# --- 設定 ---
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "credentials.json")
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "token.json")
CALENDAR_IDS = [
    "masaaki.serie@gmail.com",
    "k6ccpotlnt11kt50vl78ks95nuk2367l@import.calendar.google.com",
    "6ak4p05n1ojj27qqe9b9r7ftom33r0n8@import.calendar.google.com",
    "hebjlm5srhlikpgiu4hslgok97hh4iec@import.calendar.google.com",
]

LINE_CHANNEL_TOKEN = get_line_token()
LINE_USER_ID = "U206a030c1759f1ed8f4c684d03d11915"

OTA_PATTERNS = {
    "Booking.com": [r"booking\.com", r"booking\.com経由", r"booking"],
    "Airbnb":      [r"airbnb", r"エアビー"],
    "VRBO":        [r"vrbo", r"homeaway", r"ホームアウェイ"],
}

OTA_EMOJI = {
    "Booking.com": "🔵",
    "Airbnb":      "🔴",
    "VRBO":        "🟢",
    "Direct":      "⚪",
}

BOLD   = "\033[1m"
RESET  = "\033[0m"
BORDER = "=" * 50

COLOR_MAP = {
    "Booking.com": "\033[34m",
    "Airbnb":      "\033[31m",
    "VRBO":        "\033[32m",
    "Direct":      "\033[37m",
}

def send_line_message(message):
    data = json.dumps({"to": LINE_USER_ID, "messages": [{"type": "text", "text": message}]}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.line.me/v2/bot/message/push",
        data=data,
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + LINE_CHANNEL_TOKEN}
    )
    urllib.request.urlopen(req)

def get_calendar_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"credentials.json が見つかりません: {CREDENTIALS_FILE}\n"
                    "Google Cloud Console から OAuth 2.0 クライアント ID をダウンロードして\n"
                    f"{CREDENTIALS_FILE} に配置してください。"
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
            auth_url, _ = flow.authorization_url(prompt="consent")
            print("URLをブラウザで開いてください:")
            print(auth_url)
            code = input("認証コードを入力: ")
            flow.fetch_token(code=code)
            creds = flow.credentials
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)

def fetch_events(service, days: int = 7) -> list[dict]:
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=days)
    all_events = []
    for cal_id in CALENDAR_IDS:
        try:
            result = service.events().list(
                calendarId=cal_id,
                timeMin=now.isoformat(),
                timeMax=end.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            ).execute()
            all_events.extend(result.get("items", []))
        except Exception as e:
            print(f"カレンダー取得エラー ({cal_id}): {e}")
    return all_events

def detect_ota(text: str) -> str:
    text_lower = text.lower()
    for ota, patterns in OTA_PATTERNS.items():
        for p in patterns:
            if re.search(p, text_lower):
                return ota
    return "Direct"

def fmt_date(dt_str: str) -> str:
    if not dt_str:
        return "不明"
    try:
        if "T" in dt_str:
            dt = datetime.fromisoformat(dt_str)
            return dt.strftime("%Y-%m-%d %H:%M")
        return dt_str
    except Exception:
        return dt_str

def parse_booking(event: dict) -> dict:
    title   = event.get("summary", "（タイトルなし）")
    desc    = event.get("description", "")
    start   = event.get("start", {})
    end     = event.get("end", {})
    checkin  = start.get("dateTime") or start.get("date")
    checkout = end.get("dateTime")   or end.get("date")
    nights  = None
    if checkin and checkout:
        try:
            d1 = datetime.fromisoformat(checkin.split("T")[0])
            d2 = datetime.fromisoformat(checkout.split("T")[0])
            nights = (d2 - d1).days
        except Exception:
            pass
    combined = f"{title} {desc}"
    ota = detect_ota(combined)
    guest = re.search(r"(?:guest|ゲスト)[:\s]*([^\n,]+)", combined, re.IGNORECASE)
    guest_name = guest.group(1).strip() if guest else "不明"
    return {
        "title":    title,
        "checkin":  checkin,
        "checkout": checkout,
        "nights":   nights,
        "guest":    guest_name,
        "ota":      ota,
    }

def print_bookings(bookings: list[dict]):
    if not bookings:
        print("今後7日間の予約はありません。")
        return
    print(f"\n{BOLD}今後7日間の予約一覧{RESET}")
    print(BORDER)
    for i, b in enumerate(bookings, 1):
        ota   = b["ota"]
        color = COLOR_MAP.get(ota, "")
        tag   = f"[{ota}]"
        print(f"{BOLD}[ 予約 {i:02d}] {RESET} {tag}")
        print(f"  タイトル     : {b['title']}")
        print(f"  チェックイン : {fmt_date(b['checkin'])}")
        print(f"  チェックアウト: {fmt_date(b['checkout'])}")
        print(f"  宿泊日数     : {b['nights']} 泊" if b["nights"] is not None else "  宿泊日数     : 不明")
        print(f"  ゲスト名     : {b['guest']}")
        print(f"  OTA          : {color}{ota}{RESET}")
        print()

def format_bookings_for_line(bookings: list[dict]) -> str:
    today = datetime.now().strftime("%Y/%m/%d")
    if not bookings:
        return f"【SERIE予約確認】{today}\n\n今後7日間の予約はありません。"
    msg = f"【SERIE予約確認】{today}\n今後7日間：{len(bookings)}件\n\n"
    for b in bookings:
        emoji = OTA_EMOJI.get(b["ota"], "⚪")
        nights = f"{b['nights']}泊" if b["nights"] is not None else "不明"
        msg += f"{emoji}{b['ota']}\n"
        msg += f"　{b['title']}\n"
        msg += f"　{fmt_date(b['checkin'])} 〜 {fmt_date(b['checkout'])}（{nights}）\n\n"
    return msg.strip()

def main():
    print("Google Calendar に接続中 ...")
    service = get_calendar_service()
    print("今後7日間の予約イベントを取得中 ...")
    events = fetch_events(service, days=7)
    bookings = [parse_booking(e) for e in events]
    print_bookings(bookings)
    line_msg = format_bookings_for_line(bookings)
    send_line_message(line_msg)
    print("LINE送信完了！")

if __name__ == "__main__":
    main()
