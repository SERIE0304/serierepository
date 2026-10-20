"""旅館の予約カレンダー（iCal）から、経営ダッシュボードの宿泊記録（Firebase /guests）を自動登録する。

- チェックイン前日以降の予約だけを登録する（先の予約のキャンセルを拾わないため）
- 人数・国は iCal に入っていないので空のまま登録し、needsReview=True で「要確認」にする
- 同期の履歴は /guestSync に残す。手で直した項目は上書きせず、手で削除した記録は再登録しない

環境変数
  ICAL_FEEDS      1行に「予約経路 URL」。優先する経路から順に書く（同じ日程の重複は先の行を残す）
  FIREBASE_SA     サービスアカウントの JSON（文字列またはファイルパス）
  FIREBASE_DB_URL 省略時は serie-concerto の Realtime Database
  SYNC_SINCE      これより前のチェックインは無視（YYYY-MM-DD、省略時は11か月前の月初）

使い方: python guest_sync.py [--dry-run]
"""
import hashlib
import json
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone

import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account

JST = timezone(timedelta(hours=9))
DB_URL = os.environ.get("FIREBASE_DB_URL", "https://serie-concerto-default-rtdb.asia-southeast1.firebasedatabase.app").rstrip("/")
SCOPES = ["https://www.googleapis.com/auth/firebase.database", "https://www.googleapis.com/auth/userinfo.email"]

# 予約ではなく「売り止め・ブロック」を表すタイトル（経路ごと）
BLOCK_PATTERNS = {
    "Airbnb": [r"not available", r"blocked"],
    "Vrbo": [r"^blocked"],
}
# Booking.com は予約も売り止めも「CLOSED - Not available」なので、長期の売り止めは泊数で除外する
MAX_NIGHTS = 14
# Booking.com は当日分を書き出さないため、前日のうちに拾う
LOOKAHEAD_DAYS = 1


# ── iCal ──
def parse_ical(text: str) -> list[dict]:
    lines = []
    for raw in text.replace("\r\n", "\n").split("\n"):
        if raw[:1] in (" ", "\t") and lines:
            lines[-1] += raw[1:]
        else:
            lines.append(raw)
    events, cur = [], None
    for line in lines:
        if line == "BEGIN:VEVENT":
            cur = {}
        elif line == "END:VEVENT":
            if cur is not None:
                events.append(cur)
            cur = None
        elif cur is not None and ":" in line:
            name, value = line.split(":", 1)
            cur[name.split(";")[0].upper()] = value.replace("\\,", ",").replace("\\n", " ").strip()
    return events


def ical_date(v: str) -> date | None:
    m = re.match(r"(\d{4})(\d{2})(\d{2})", v or "")
    return date(int(m[1]), int(m[2]), int(m[3])) if m else None


def load_feeds() -> list[tuple[str, str]]:
    feeds = []
    for line in os.environ.get("ICAL_FEEDS", "").splitlines():
        line = line.strip().lstrip("﻿")
        if not line or line.startswith("#"):
            continue
        name, _, url = line.rpartition(" ")
        if name.strip() and url.startswith("http"):
            feeds.append((name.strip(), url))
    if not feeds:
        sys.exit("ICAL_FEEDS が空です")
    return feeds


def fetch_stays(feeds, since: date, today: date) -> list[dict]:
    stays, seen = [], set()
    for channel, url in feeds:
        r = requests.get(url, timeout=30, headers={"User-Agent": "serie-guest-sync"})
        r.raise_for_status()
        blocks = BLOCK_PATTERNS.get(channel, [])
        for ev in parse_ical(r.text):
            ci, co = ical_date(ev.get("DTSTART")), ical_date(ev.get("DTEND"))
            summary = ev.get("SUMMARY", "")
            if not ci or not co or co <= ci or (co - ci).days > MAX_NIGHTS:
                continue
            if any(re.search(p, summary, re.IGNORECASE) for p in blocks):
                continue
            if ci < since or ci > today:
                continue
            if (ci, co) in seen:  # 別の経路から取り込まれた同じ予約
                print(f"  重複のため除外: {channel} {ci}〜{co} {summary}")
                continue
            seen.add((ci, co))
            uid = ev.get("UID") or f"{ci}-{co}"
            key = hashlib.sha1(f"{channel}|{uid}".encode()).hexdigest()[:20]
            stays.append({"key": key, "channel": channel, "checkIn": ci.isoformat(),
                          "nights": (co - ci).days, "summary": summary})
    return stays


# ── Firebase ──
class DB:
    def __init__(self, sa: str, dry: bool):
        # 秘密鍵がエラー表示に出ないよう、中身は例外メッセージに含めない
        sa = sa.strip().lstrip("﻿")
        try:
            info = json.loads(sa) if sa.startswith("{") else json.load(open(sa, encoding="utf-8-sig"))
        except Exception:
            sys.exit("FIREBASE_SA を読み込めません（JSON またはファイルパスを指定してください）")
        self.creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
        self.dry = dry

    def _h(self):
        if not self.creds.valid:
            self.creds.refresh(Request())
        return {"Authorization": f"Bearer {self.creds.token}"}

    def get(self, path):
        r = requests.get(f"{DB_URL}/{path}.json", headers=self._h(), timeout=30)
        r.raise_for_status()
        return r.json() or {}

    def write(self, method, path, data):
        if self.dry:
            print(f"  [dry-run] {method} {path} {json.dumps(data, ensure_ascii=False)}")
            return {"name": "(dry-run)"}
        r = requests.request(method, f"{DB_URL}/{path}.json", headers=self._h(), json=data, timeout=30)
        r.raise_for_status()
        return r.json()


def main():
    dry = "--dry-run" in sys.argv
    today = datetime.now(JST).date()
    since_env = os.environ.get("SYNC_SINCE")
    if since_env:
        since = date.fromisoformat(since_env)
    else:
        y, m = today.year, today.month - 11
        while m < 1:
            y, m = y - 1, m + 12
        since = date(y, m, 1)

    until = today + timedelta(days=LOOKAHEAD_DAYS)
    stays = fetch_stays(load_feeds(), since, until)
    print(f"{since}〜{until} のチェックイン: {len(stays)}件")

    db = DB(os.environ["FIREBASE_SA"], dry)
    synced, guests = db.get("guestSync"), db.get("guests")
    added = updated = 0
    for s in stays:
        prev = synced.get(s["key"])
        if prev is None:
            res = db.write("POST", "guests", {
                "checkIn": s["checkIn"], "nights": s["nights"], "adults": 0, "children": 0,
                "country": "", "channel": s["channel"], "memo": "",
                "source": "calendar", "needsReview": True,
                "createdAt": {".sv": "timestamp"}, "createdBy": "calendar-sync",
            })
            db.write("PUT", f"guestSync/{s['key']}", {
                "guestId": res["name"], "checkIn": s["checkIn"], "nights": s["nights"],
                "channel": s["channel"],
            })
            added += 1
            print(f"  追加: {s['checkIn']} {s['nights']}泊 {s['channel']}")
            continue
        g = guests.get(prev.get("guestId"))
        if g is None:  # ダッシュボードで削除された記録は戻さない
            continue
        # 前回の同期から手で変えていない項目だけ、カレンダーの変更（日程変更など）に合わせる
        patch = {f: s[f] for f in ("checkIn", "nights", "channel")
                 if s[f] != prev.get(f) and g.get(f) == prev.get(f)}
        if patch:
            db.write("PATCH", f"guests/{prev['guestId']}", patch)
            db.write("PATCH", f"guestSync/{s['key']}", patch)
            updated += 1
            print(f"  更新: {s['checkIn']} {s['channel']} {patch}")
    print(f"追加 {added}件・更新 {updated}件" + ("（dry-run）" if dry else ""))


if __name__ == "__main__":
    main()
